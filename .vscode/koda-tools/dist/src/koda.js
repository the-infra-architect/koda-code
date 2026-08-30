"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KodaService = void 0;
const contracts_js_1 = require("./contracts.js");
const engine_js_1 = require("./engine.js");
const workspace_js_1 = require("./workspace.js");
const mutationLocks = new Set();
const MUTATING = new Set(["begin", "answer", "record", "check"]);
const MAX_JSON_BYTES = 262_144;
class KodaService {
    engineResolver;
    jsonRunner;
    constructor(engineResolver = engine_js_1.resolveEngine, jsonRunner = engine_js_1.runJson) {
        this.engineResolver = engineResolver;
        this.jsonRunner = jsonRunner;
    }
    async invoke(operation, rawInput, settings, cancellation) {
        let workspace = "";
        try {
            const input = (0, contracts_js_1.recordValue)(rawInput);
            const repository = (0, contracts_js_1.optionalString)(input, "repository", 4096);
            workspace = await (0, workspace_js_1.selectWorkspace)(settings.workspaceRoots, repository);
            const args = this.arguments(operation, input, workspace);
            if (MUTATING.has(operation) && mutationLocks.has(workspace)) {
                throw new contracts_js_1.InputError("Another mutating Koda invocation is already running for this workspace.");
            }
            if (MUTATING.has(operation))
                mutationLocks.add(workspace);
            try {
                const engine = await this.engineResolver(workspace, settings.enginePath);
                const data = await this.jsonRunner(engine, args, workspace, {
                    timeoutMilliseconds: normalizeTimeout(settings.timeoutSeconds),
                    maxOutputBytes: MAX_JSON_BYTES,
                    cancellation,
                });
                return { ok: true, operation, data };
            }
            finally {
                if (MUTATING.has(operation))
                    mutationLocks.delete(workspace);
            }
        }
        catch (error) {
            const code = error instanceof engine_js_1.EngineError
                ? error.code
                : error instanceof contracts_js_1.InputError
                    ? "invalid_input"
                    : "unexpected";
            const message = error instanceof Error ? error.message : "Unexpected Koda extension error.";
            return { ok: false, operation, error: { code, message: bounded(message, 4000) } };
        }
    }
    arguments(operation, input, workspace) {
        switch (operation) {
            case "project":
                return ["project", "--repo", workspace, "--json"];
            case "begin":
                return [
                    "begin",
                    (0, contracts_js_1.requiredString)(input, "request", 20_000),
                    "--repo",
                    workspace,
                    "--prepare-worktree",
                    "--json",
                ];
            case "status":
                return ["status", (0, contracts_js_1.missionId)(input), "--repo", workspace, "--json"];
            case "evidence":
                return ["evidence", (0, contracts_js_1.missionId)(input), "--repo", workspace, "--json"];
            case "check":
                return ["check", (0, contracts_js_1.missionId)(input), "--repo", workspace, "--json"];
            case "answer":
                return [
                    "answer",
                    (0, contracts_js_1.missionId)(input),
                    "--repo",
                    workspace,
                    "--answer",
                    (0, contracts_js_1.requiredString)(input, "answer", 4000),
                    "--json",
                ];
            case "record": {
                const agent = (0, contracts_js_1.oneOf)(input, "agent", contracts_js_1.AGENTS);
                const outcome = (0, contracts_js_1.oneOf)(input, "outcome", contracts_js_1.OUTCOMES);
                const args = [
                    "record",
                    (0, contracts_js_1.missionId)(input),
                    "--repo",
                    workspace,
                    "--agent",
                    agent,
                    "--outcome",
                    outcome,
                    "--note",
                    (0, contracts_js_1.requiredString)(input, "note", 4000),
                    "--verified-evidence",
                    "--json",
                ];
                const fingerprint = (0, contracts_js_1.evidenceFingerprint)(input);
                if (fingerprint !== undefined)
                    args.push("--evidence-fingerprint", fingerprint);
                if ((0, contracts_js_1.optionalBoolean)(input, "unclearFailure"))
                    args.push("--unclear-failure");
                return args;
            }
        }
    }
}
exports.KodaService = KodaService;
function normalizeTimeout(seconds) {
    if (!Number.isFinite(seconds) || seconds < 1 || seconds > 1800) {
        return 300_000;
    }
    return Math.floor(seconds * 1000);
}
function bounded(value, maximum) {
    if (value.length <= maximum)
        return value;
    const half = Math.floor(maximum / 2);
    return `${value.slice(0, half)}\n... truncated ...\n${value.slice(-half)}`;
}
//# sourceMappingURL=koda.js.map