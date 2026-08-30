"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const contracts_js_1 = require("./contracts.js");
const koda_js_1 = require("./koda.js");
const TOOL_NAMES = {
    project: "koda-code_project",
    begin: "koda-code_begin",
    answer: "koda-code_answer",
    status: "koda-code_status",
    evidence: "koda-code_evidence",
    record: "koda-code_record",
    check: "koda-code_check",
};
const MUTATING = new Set(["begin", "answer", "record", "check"]);
class KodaLanguageModelTool {
    operation;
    service;
    constructor(operation, service) {
        this.operation = operation;
        this.service = service;
    }
    async invoke(options, token) {
        const configuration = vscode.workspace.getConfiguration("koda");
        const enginePath = configuration.get("enginePath")?.trim() || undefined;
        const timeoutSeconds = configuration.get("engineTimeoutSeconds", 300);
        const roots = (vscode.workspace.workspaceFolders ?? []).map((folder) => folder.uri.fsPath);
        const result = await this.service.invoke(this.operation, options.input, { workspaceRoots: roots, enginePath, timeoutSeconds }, token);
        return new vscode.LanguageModelToolResult([
            new vscode.LanguageModelTextPart(JSON.stringify(result)),
        ]);
    }
    prepareInvocation(options) {
        const subject = subjectFor(this.operation, options.input);
        const prepared = {
            invocationMessage: `${label(this.operation)} ${subject}`.trim(),
        };
        if (MUTATING.has(this.operation)) {
            prepared.confirmationMessages = {
                title: `${label(this.operation)}?`,
                message: confirmation(this.operation, subject),
            };
        }
        return prepared;
    }
}
function activate(context) {
    const service = new koda_js_1.KodaService();
    for (const [operation, name] of Object.entries(TOOL_NAMES)) {
        context.subscriptions.push(vscode.lm.registerTool(name, new KodaLanguageModelTool(operation, service)));
    }
}
function deactivate() { }
function subjectFor(operation, rawInput) {
    try {
        const input = (0, contracts_js_1.recordValue)(rawInput);
        const candidate = operation === "begin" ? input.request : input.missionId;
        if (typeof candidate !== "string")
            return "";
        return candidate.replace(/[\r\n\t]+/gu, " ").slice(0, 120);
    }
    catch {
        return "";
    }
}
function label(operation) {
    return {
        project: "Inspecting Koda project",
        begin: "Beginning Koda mission",
        answer: "Recording Koda clarification",
        status: "Reading Koda mission status",
        evidence: "Reading Koda Git evidence",
        record: "Recording verified Koda result",
        check: "Running Koda quality gate",
    }[operation];
}
function confirmation(operation, subject) {
    const action = {
        begin: "create an isolated Git worktree and local mission state for",
        answer: "record the user's product clarification for",
        record: "update verified local mission state for",
        check: "run the argv-based quality checks configured by the project for",
        project: "inspect",
        status: "inspect",
        evidence: "inspect",
    }[operation];
    return new vscode.MarkdownString(`Koda will ${action} **${escapeMarkdown(subject || "this mission")}**.`);
}
function escapeMarkdown(value) {
    return value.replace(/[\\`*_{}[\]()<>#+\-.!|]/gu, "\\$&");
}
//# sourceMappingURL=extension.js.map