import * as vscode from "vscode";

import { recordValue, type KodaOperation } from "./contracts.js";
import { KodaService } from "./koda.js";

const TOOL_NAMES: Readonly<Record<KodaOperation, string>> = {
  project: "koda-code_project",
  begin: "koda-code_begin",
  answer: "koda-code_answer",
  status: "koda-code_status",
  evidence: "koda-code_evidence",
  record: "koda-code_record",
  check: "koda-code_check",
};
const MUTATING = new Set<KodaOperation>(["begin", "answer", "record", "check"]);

class KodaLanguageModelTool implements vscode.LanguageModelTool<unknown> {
  public constructor(
    private readonly operation: KodaOperation,
    private readonly service: KodaService,
  ) {}

  public async invoke(
    options: vscode.LanguageModelToolInvocationOptions<unknown>,
    token: vscode.CancellationToken,
  ): Promise<vscode.LanguageModelToolResult> {
    const configuration = vscode.workspace.getConfiguration("koda");
    const enginePath = configuration.get<string>("enginePath")?.trim() || undefined;
    const timeoutSeconds = configuration.get<number>("engineTimeoutSeconds", 300);
    const roots = (vscode.workspace.workspaceFolders ?? []).map((folder) => folder.uri.fsPath);
    const result = await this.service.invoke(
      this.operation,
      options.input,
      { workspaceRoots: roots, enginePath, timeoutSeconds },
      token,
    );
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(JSON.stringify(result)),
    ]);
  }

  public prepareInvocation(
    options: vscode.LanguageModelToolInvocationPrepareOptions<unknown>,
  ): vscode.PreparedToolInvocation {
    const subject = subjectFor(this.operation, options.input);
    const prepared: vscode.PreparedToolInvocation = {
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

export function activate(context: vscode.ExtensionContext): void {
  const service = new KodaService();
  for (const [operation, name] of Object.entries(TOOL_NAMES) as [KodaOperation, string][]) {
    context.subscriptions.push(vscode.lm.registerTool(name, new KodaLanguageModelTool(operation, service)));
  }
}

export function deactivate(): void {}

function subjectFor(operation: KodaOperation, rawInput: unknown): string {
  try {
    const input = recordValue(rawInput);
    const candidate = operation === "begin" ? input.request : input.missionId;
    if (typeof candidate !== "string") return "";
    return candidate.replace(/[\r\n\t]+/gu, " ").slice(0, 120);
  } catch {
    return "";
  }
}

function label(operation: KodaOperation): string {
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

function confirmation(operation: KodaOperation, subject: string): vscode.MarkdownString {
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

function escapeMarkdown(value: string): string {
  return value.replace(/[\\`*_{}[\]()<>#+\-.!|]/gu, "\\$&");
}
