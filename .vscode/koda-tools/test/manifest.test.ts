import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import test from "node:test";

interface ToolContribution {
  name: string;
  canBeReferencedInPrompt?: boolean;
  modelDescription?: string;
  toolReferenceName?: string;
  inputSchema?: object;
}

interface AgentContribution {
  path: string;
}

test("extension manifest exposes the bounded Koda tool surface", async () => {
  const path = resolve(__dirname, "../../package.json");
  const manifest = JSON.parse(await readFile(path, "utf8")) as {
    activationEvents: string[];
    files: string[];
    main: string;
    contributes: {
      chatAgents: AgentContribution[];
      languageModelTools: ToolContribution[];
    };
  };
  assert.deepEqual(
    manifest.contributes.chatAgents.map((agent) => agent.path),
    [
      "./agents/koda.agent.md",
      "./agents/engineer.agent.md",
      "./agents/ui-ux.agent.md",
      "./agents/tester.agent.md",
      "./agents/reviewer.agent.md",
      "./agents/debugger.agent.md",
    ],
  );
  const tools = manifest.contributes.languageModelTools;
  assert.deepEqual(
    tools.map((tool) => [tool.name, tool.toolReferenceName]),
    [
      ["koda-code_project", "kodaProject"],
      ["koda-code_begin", "kodaBegin"],
      ["koda-code_answer", "kodaAnswer"],
      ["koda-code_status", "kodaStatus"],
      ["koda-code_evidence", "kodaEvidence"],
      ["koda-code_record", "kodaRecord"],
      ["koda-code_check", "kodaCheck"],
    ],
  );
  assert.ok(
    tools.every(
      (tool) =>
        tool.canBeReferencedInPrompt === true &&
        typeof tool.modelDescription === "string" &&
        tool.modelDescription.length > 20 &&
        tool.inputSchema !== undefined,
    ),
  );
  assert.equal(manifest.main, "./dist/src/extension.js");
  assert.ok(manifest.files.includes("dist/src/**"));
  assert.ok(manifest.files.includes("agents/**"));
  assert.deepEqual(
    manifest.activationEvents,
    tools.map((tool) => `onLanguageModelTool:${tool.name}`),
  );
});
