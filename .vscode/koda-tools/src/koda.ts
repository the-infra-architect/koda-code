import {
  AGENTS,
  evidenceFingerprint,
  InputError,
  missionId,
  oneOf,
  optionalBoolean,
  optionalString,
  OUTCOMES,
  recordValue,
  requiredString,
  type KodaOperation,
} from "./contracts.js";
import {
  EngineError,
  resolveEngine,
  runJson,
  type CancellationLike,
  type EngineCommand,
  type ProcessOptions,
} from "./engine.js";
import { selectWorkspace } from "./workspace.js";

export interface KodaSettings {
  readonly workspaceRoots: readonly string[];
  readonly enginePath?: string;
  readonly timeoutSeconds: number;
}

export interface ToolResult {
  readonly ok: boolean;
  readonly operation: KodaOperation;
  readonly data?: unknown;
  readonly error?: {
    readonly code: string;
    readonly message: string;
  };
}

export type EngineResolver = (
  workspace: string,
  configuredPath: string | undefined,
) => Promise<EngineCommand>;
export type JsonRunner = (
  command: EngineCommand,
  args: readonly string[],
  cwd: string,
  options: ProcessOptions,
) => Promise<unknown>;

const mutationLocks = new Set<string>();
const MUTATING = new Set<KodaOperation>(["begin", "answer", "record", "check"]);
const MAX_JSON_BYTES = 262_144;

export class KodaService {
  public constructor(
    private readonly engineResolver: EngineResolver = resolveEngine,
    private readonly jsonRunner: JsonRunner = runJson,
  ) {}

  public async invoke(
    operation: KodaOperation,
    rawInput: unknown,
    settings: KodaSettings,
    cancellation?: CancellationLike,
  ): Promise<ToolResult> {
    let workspace = "";
    try {
      const input = recordValue(rawInput);
      const repository = optionalString(input, "repository", 4096);
      workspace = await selectWorkspace(settings.workspaceRoots, repository);
      const args = this.arguments(operation, input, workspace);
      if (MUTATING.has(operation) && mutationLocks.has(workspace)) {
        throw new InputError("Another mutating Koda invocation is already running for this workspace.");
      }
      if (MUTATING.has(operation)) mutationLocks.add(workspace);
      try {
        const engine = await this.engineResolver(workspace, settings.enginePath);
        const data = await this.jsonRunner(engine, args, workspace, {
          timeoutMilliseconds: normalizeTimeout(settings.timeoutSeconds),
          maxOutputBytes: MAX_JSON_BYTES,
          cancellation,
        });
        return { ok: true, operation, data };
      } finally {
        if (MUTATING.has(operation)) mutationLocks.delete(workspace);
      }
    } catch (error) {
      const code =
        error instanceof EngineError
          ? error.code
          : error instanceof InputError
            ? "invalid_input"
            : "unexpected";
      const message = error instanceof Error ? error.message : "Unexpected Koda extension error.";
      return { ok: false, operation, error: { code, message: bounded(message, 4000) } };
    }
  }

  private arguments(
    operation: KodaOperation,
    input: Record<string, unknown>,
    workspace: string,
  ): readonly string[] {
    switch (operation) {
      case "project":
        return ["project", "--repo", workspace, "--json"];
      case "begin":
        return [
          "begin",
          requiredString(input, "request", 20_000),
          "--repo",
          workspace,
          "--prepare-worktree",
          "--json",
        ];
      case "status":
        return ["status", missionId(input), "--repo", workspace, "--json"];
      case "evidence":
        return ["evidence", missionId(input), "--repo", workspace, "--json"];
      case "check":
        return ["check", missionId(input), "--repo", workspace, "--json"];
      case "answer":
        return [
          "answer",
          missionId(input),
          "--repo",
          workspace,
          "--answer",
          requiredString(input, "answer", 4000),
          "--json",
        ];
      case "record": {
        const agent = oneOf(input, "agent", AGENTS);
        const outcome = oneOf(input, "outcome", OUTCOMES);
        const args = [
          "record",
          missionId(input),
          "--repo",
          workspace,
          "--agent",
          agent,
          "--outcome",
          outcome,
          "--note",
          requiredString(input, "note", 4000),
          "--verified-evidence",
          "--json",
        ];
        const fingerprint = evidenceFingerprint(input);
        if (fingerprint !== undefined) args.push("--evidence-fingerprint", fingerprint);
        if (optionalBoolean(input, "unclearFailure")) args.push("--unclear-failure");
        return args;
      }
    }
  }
}

function normalizeTimeout(seconds: number): number {
  if (!Number.isFinite(seconds) || seconds < 1 || seconds > 1800) {
    return 300_000;
  }
  return Math.floor(seconds * 1000);
}

function bounded(value: string, maximum: number): string {
  if (value.length <= maximum) return value;
  const half = Math.floor(maximum / 2);
  return `${value.slice(0, half)}\n... truncated ...\n${value.slice(-half)}`;
}
