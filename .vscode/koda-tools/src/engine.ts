import { constants } from "node:fs";
import { access, readFile } from "node:fs/promises";
import { delimiter, isAbsolute, join, resolve } from "node:path";
import { spawn } from "node:child_process";

export interface CancellationLike {
  readonly isCancellationRequested: boolean;
  onCancellationRequested(listener: () => void): { dispose(): void };
}

export interface EngineCommand {
  readonly executable: string;
  readonly prefix: readonly string[];
  readonly source: "configured" | "workspace" | "path" | "development";
  readonly version: string;
}

export interface ProcessOptions {
  readonly timeoutMilliseconds: number;
  readonly maxOutputBytes: number;
  readonly cancellation?: CancellationLike;
}

export class EngineError extends Error {
  public constructor(
    public readonly code:
      | "missing"
      | "invalid"
      | "incompatible"
      | "failed"
      | "timed_out"
      | "cancelled"
      | "malformed_output"
      | "output_limit",
    message: string,
  ) {
    super(message);
    this.name = "EngineError";
  }
}

const SAFE_ENVIRONMENT = new Set([
  "PATH",
  "SYSTEMROOT",
  "TMPDIR",
  "TMP",
  "TEMP",
  "USERPROFILE",
  "LANG",
  "LC_ALL",
]);
const VERSION_PATTERN = /Koda-Code\s+(\d+)\.(\d+)\.(\d+)/u;
const MINIMUM_ENGINE_VERSION = "0.4.0";

function environment(): NodeJS.ProcessEnv {
  return Object.fromEntries(
    Object.entries(process.env).filter(([key]) => SAFE_ENVIRONMENT.has(key)),
  );
}

export async function runProcess(
  command: EngineCommand,
  args: readonly string[],
  cwd: string,
  options: ProcessOptions,
): Promise<string> {
  if (options.cancellation?.isCancellationRequested === true) {
    throw new EngineError("cancelled", "Koda invocation was cancelled before it started.");
  }
  return new Promise<string>((resolvePromise, rejectPromise) => {
    const child = spawn(command.executable, [...command.prefix, ...args], {
      cwd,
      detached: process.platform !== "win32",
      env: environment(),
      shell: false,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    let bytes = 0;
    let settled = false;
    let timeout: NodeJS.Timeout | undefined = undefined;
    let cancellation = { dispose: (): void => undefined };
    const terminate = (): void => {
      if (process.platform !== "win32" && child.pid !== undefined) {
        try {
          process.kill(-child.pid, "SIGTERM");
          return;
        } catch {
          // Fall through to terminating the direct child.
        }
      }
      child.kill();
    };
    const finish = (error?: EngineError, output?: string): void => {
      if (settled) return;
      settled = true;
      if (timeout !== undefined) clearTimeout(timeout);
      cancellation.dispose();
      if (error !== undefined) rejectPromise(error);
      else resolvePromise(output ?? "");
    };
    const append = (target: "stdout" | "stderr", chunk: Buffer): void => {
      bytes += chunk.byteLength;
      if (bytes > options.maxOutputBytes) {
        terminate();
        finish(new EngineError("output_limit", "Koda engine output exceeded the safe limit."));
        return;
      }
      if (target === "stdout") stdout += chunk.toString("utf8");
      else stderr += chunk.toString("utf8");
    };
    child.stdout.on("data", (chunk: Buffer) => append("stdout", chunk));
    child.stderr.on("data", (chunk: Buffer) => append("stderr", chunk));
    child.on("error", (error) => {
      finish(
        new EngineError(
          error.message.includes("ENOENT") ? "missing" : "failed",
          `Could not start Koda engine: ${error.message}`,
        ),
      );
    });
    child.on("close", (code) => {
      if (settled) return;
      if (code !== 0) {
        const detail = [stdout, stderr].map((part) => part.trim()).filter(Boolean).join("\n");
        finish(new EngineError("failed", detail || `Koda engine exited with code ${String(code)}.`));
        return;
      }
      finish(undefined, stdout);
    });
    timeout = setTimeout(() => {
      terminate();
      finish(new EngineError("timed_out", "Koda engine invocation timed out."));
    }, options.timeoutMilliseconds);
    cancellation =
      options.cancellation?.onCancellationRequested(() => {
        terminate();
        finish(new EngineError("cancelled", "Koda engine invocation was cancelled."));
      }) ?? { dispose: (): void => undefined };
  });
}

async function executable(path: string): Promise<boolean> {
  try {
    await access(path, process.platform === "win32" ? constants.F_OK : constants.X_OK);
    return true;
  } catch {
    return false;
  }
}

function parseVersion(output: string): string {
  const match = VERSION_PATTERN.exec(output);
  if (match === null) {
    throw new EngineError("invalid", "The selected executable is not a Koda-Code engine.");
  }
  const major = Number(match[1]);
  const minor = Number(match[2]);
  if (major === 0 && minor < 4) {
    throw new EngineError(
      "incompatible",
      `Koda-Code ${match[1]}.${match[2]}.${match[3]} is incompatible; version ${MINIMUM_ENGINE_VERSION}+ is required.`,
    );
  }
  return `${match[1]}.${match[2]}.${match[3]}`;
}

async function inspectCandidate(
  executablePath: string,
  prefix: readonly string[],
  source: EngineCommand["source"],
  workspace: string,
): Promise<EngineCommand> {
  const provisional: EngineCommand = {
    executable: executablePath,
    prefix,
    source,
    version: "unknown",
  };
  const output = await runProcess(provisional, ["--version"], workspace, {
    timeoutMilliseconds: 10_000,
    maxOutputBytes: 8192,
  });
  return { ...provisional, version: parseVersion(output) };
}

export async function resolveEngine(
  workspace: string,
  configuredPath: string | undefined,
): Promise<EngineCommand> {
  if (configuredPath !== undefined && configuredPath.trim() !== "") {
    const selected = isAbsolute(configuredPath)
      ? configuredPath
      : resolve(workspace, configuredPath);
    if (!(await executable(selected))) {
      throw new EngineError("invalid", `Configured Koda executable is not runnable: ${selected}`);
    }
    return inspectCandidate(selected, [], "configured", workspace);
  }

  const local = join(workspace, ".venv", process.platform === "win32" ? "Scripts/koda.exe" : "bin/koda");
  if (await executable(local)) {
    return inspectCandidate(local, [], "workspace", workspace);
  }

  try {
    return await inspectCandidate("koda", [], "path", workspace);
  } catch (error) {
    if (!(error instanceof EngineError) || error.code !== "missing") throw error;
  }

  const python = join(
    workspace,
    ".venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
  );
  const project = join(workspace, "pyproject.toml");
  if (await executable(python)) {
    try {
      const configuration = await readFile(project, "utf8");
      if (/name\s*=\s*["']koda-code["']/u.test(configuration)) {
        return inspectCandidate(python, ["-m", "koda_code"], "development", workspace);
      }
    } catch {
      // The deterministic fallbacks are exhausted below.
    }
  }
  const searched = (process.env.PATH ?? "").split(delimiter).filter(Boolean).length;
  throw new EngineError(
    "missing",
    `Koda ${MINIMUM_ENGINE_VERSION}+ was not found in koda.enginePath, .venv, or PATH (${String(searched)} PATH entries checked). Install Koda explicitly; the extension never downloads it.`,
  );
}

export async function runJson(
  command: EngineCommand,
  args: readonly string[],
  cwd: string,
  options: ProcessOptions,
): Promise<unknown> {
  const output = await runProcess(command, args, cwd, options);
  try {
    const parsed = JSON.parse(output) as unknown;
    if (typeof parsed !== "object" || parsed === null) {
      throw new Error("JSON result is not structured.");
    }
    return parsed;
  } catch {
    throw new EngineError("malformed_output", "Koda engine returned malformed JSON.");
  }
}
