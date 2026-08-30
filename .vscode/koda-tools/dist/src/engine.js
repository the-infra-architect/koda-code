"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EngineError = void 0;
exports.runProcess = runProcess;
exports.resolveEngine = resolveEngine;
exports.runJson = runJson;
const node_fs_1 = require("node:fs");
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const node_child_process_1 = require("node:child_process");
class EngineError extends Error {
    code;
    constructor(code, message) {
        super(message);
        this.code = code;
        this.name = "EngineError";
    }
}
exports.EngineError = EngineError;
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
function environment() {
    return Object.fromEntries(Object.entries(process.env).filter(([key]) => SAFE_ENVIRONMENT.has(key)));
}
async function runProcess(command, args, cwd, options) {
    if (options.cancellation?.isCancellationRequested === true) {
        throw new EngineError("cancelled", "Koda invocation was cancelled before it started.");
    }
    return new Promise((resolvePromise, rejectPromise) => {
        const child = (0, node_child_process_1.spawn)(command.executable, [...command.prefix, ...args], {
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
        let timeout = undefined;
        let cancellation = { dispose: () => undefined };
        const terminate = () => {
            if (process.platform !== "win32" && child.pid !== undefined) {
                try {
                    process.kill(-child.pid, "SIGTERM");
                    return;
                }
                catch {
                    // Fall through to terminating the direct child.
                }
            }
            child.kill();
        };
        const finish = (error, output) => {
            if (settled)
                return;
            settled = true;
            if (timeout !== undefined)
                clearTimeout(timeout);
            cancellation.dispose();
            if (error !== undefined)
                rejectPromise(error);
            else
                resolvePromise(output ?? "");
        };
        const append = (target, chunk) => {
            bytes += chunk.byteLength;
            if (bytes > options.maxOutputBytes) {
                terminate();
                finish(new EngineError("output_limit", "Koda engine output exceeded the safe limit."));
                return;
            }
            if (target === "stdout")
                stdout += chunk.toString("utf8");
            else
                stderr += chunk.toString("utf8");
        };
        child.stdout.on("data", (chunk) => append("stdout", chunk));
        child.stderr.on("data", (chunk) => append("stderr", chunk));
        child.on("error", (error) => {
            finish(new EngineError(error.message.includes("ENOENT") ? "missing" : "failed", `Could not start Koda engine: ${error.message}`));
        });
        child.on("close", (code) => {
            if (settled)
                return;
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
            }) ?? { dispose: () => undefined };
    });
}
async function executable(path) {
    try {
        await (0, promises_1.access)(path, process.platform === "win32" ? node_fs_1.constants.F_OK : node_fs_1.constants.X_OK);
        return true;
    }
    catch {
        return false;
    }
}
function parseVersion(output) {
    const match = VERSION_PATTERN.exec(output);
    if (match === null) {
        throw new EngineError("invalid", "The selected executable is not a Koda-Code engine.");
    }
    const major = Number(match[1]);
    const minor = Number(match[2]);
    if (major === 0 && minor < 4) {
        throw new EngineError("incompatible", `Koda-Code ${match[1]}.${match[2]}.${match[3]} is incompatible; version ${MINIMUM_ENGINE_VERSION}+ is required.`);
    }
    return `${match[1]}.${match[2]}.${match[3]}`;
}
async function inspectCandidate(executablePath, prefix, source, workspace) {
    const provisional = {
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
async function resolveEngine(workspace, configuredPath) {
    if (configuredPath !== undefined && configuredPath.trim() !== "") {
        const selected = (0, node_path_1.isAbsolute)(configuredPath)
            ? configuredPath
            : (0, node_path_1.resolve)(workspace, configuredPath);
        if (!(await executable(selected))) {
            throw new EngineError("invalid", `Configured Koda executable is not runnable: ${selected}`);
        }
        return inspectCandidate(selected, [], "configured", workspace);
    }
    const local = (0, node_path_1.join)(workspace, ".venv", process.platform === "win32" ? "Scripts/koda.exe" : "bin/koda");
    if (await executable(local)) {
        return inspectCandidate(local, [], "workspace", workspace);
    }
    try {
        return await inspectCandidate("koda", [], "path", workspace);
    }
    catch (error) {
        if (!(error instanceof EngineError) || error.code !== "missing")
            throw error;
    }
    const python = (0, node_path_1.join)(workspace, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
    const project = (0, node_path_1.join)(workspace, "pyproject.toml");
    if (await executable(python)) {
        try {
            const configuration = await (0, promises_1.readFile)(project, "utf8");
            if (/name\s*=\s*["']koda-code["']/u.test(configuration)) {
                return inspectCandidate(python, ["-m", "koda_code"], "development", workspace);
            }
        }
        catch {
            // The deterministic fallbacks are exhausted below.
        }
    }
    const searched = (process.env.PATH ?? "").split(node_path_1.delimiter).filter(Boolean).length;
    throw new EngineError("missing", `Koda ${MINIMUM_ENGINE_VERSION}+ was not found in koda.enginePath, .venv, or PATH (${String(searched)} PATH entries checked). Install Koda explicitly; the extension never downloads it.`);
}
async function runJson(command, args, cwd, options) {
    const output = await runProcess(command, args, cwd, options);
    try {
        const parsed = JSON.parse(output);
        if (typeof parsed !== "object" || parsed === null) {
            throw new Error("JSON result is not structured.");
        }
        return parsed;
    }
    catch {
        throw new EngineError("malformed_output", "Koda engine returned malformed JSON.");
    }
}
//# sourceMappingURL=engine.js.map