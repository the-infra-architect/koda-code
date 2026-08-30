import assert from "node:assert/strict";
import { mkdir, mkdtemp, realpath } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { EngineError, type EngineCommand } from "../src/engine.js";
import { KodaService, type JsonRunner } from "../src/koda.js";

const ENGINE: EngineCommand = {
  executable: "koda",
  prefix: [],
  source: "path",
  version: "0.4.0",
};

async function workspace(): Promise<string> {
  const directory = await mkdtemp(join(tmpdir(), "koda-service-"));
  const root = join(directory, "project");
  await mkdir(root);
  return root;
}

test("service constructs argv without a shell and validates model input", async () => {
  const root = await workspace();
  let observed: readonly string[] = [];
  const runner: JsonRunner = async (_engine, args) => {
    observed = args;
    return { mission_id: "mission-1" };
  };
  const service = new KodaService(async () => ENGINE, runner);
  const result = await service.invoke(
    "begin",
    { request: "Improve error handling" },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.equal(result.ok, true);
  assert.deepEqual(observed, [
    "begin",
    "Improve error handling",
    "--repo",
    await realpath(root),
    "--prepare-worktree",
    "--json",
  ]);
  const invalid = await service.invoke(
    "status",
    { missionId: "../escape" },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.deepEqual(invalid.error?.code, "invalid_input");
});

test("record validates enums and passes verified evidence flags", async () => {
  const root = await workspace();
  let observed: readonly string[] = [];
  const service = new KodaService(async () => ENGINE, async (_engine, args) => {
    observed = args;
    return {};
  });
  const fingerprint = "a".repeat(64);
  const result = await service.invoke(
    "record",
    {
      missionId: "mission-1",
      agent: "reviewer",
      outcome: "needs_work",
      note: "A concrete finding.",
      evidenceFingerprint: fingerprint,
      unclearFailure: true,
    },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.equal(result.ok, true);
  assert.ok(observed.includes("--verified-evidence"));
  assert.ok(observed.includes(fingerprint));
  assert.ok(observed.includes("--unclear-failure"));
  const invalid = await service.invoke(
    "record",
    { missionId: "mission-1", agent: "manager", outcome: "passed", note: "no" },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.equal(invalid.error?.code, "invalid_input");
});

test("read, answer, and check operations map to the stable CLI contract", async () => {
  const root = await workspace();
  const calls: string[][] = [];
  const service = new KodaService(async () => ENGINE, async (_engine, args) => {
    calls.push([...args]);
    return {};
  });
  const settings = { workspaceRoots: [root], timeoutSeconds: 30 };
  assert.equal((await service.invoke("project", {}, settings)).ok, true);
  assert.equal((await service.invoke("status", { missionId: "mission-1" }, settings)).ok, true);
  assert.equal((await service.invoke("evidence", { missionId: "mission-1" }, settings)).ok, true);
  assert.equal(
    (
      await service.invoke(
        "answer",
        { missionId: "mission-1", answer: "Keep it local." },
        settings,
      )
    ).ok,
    true,
  );
  assert.equal((await service.invoke("check", { missionId: "mission-1" }, settings)).ok, true);
  assert.deepEqual(
    calls.map((call) => call[0]),
    ["project", "status", "evidence", "answer", "check"],
  );
  assert.ok(calls[3]?.includes("Keep it local."));
});

test("engine discovery failures become concise structured tool errors", async () => {
  const root = await workspace();
  const service = new KodaService(async () => {
    throw new EngineError("missing", "Koda engine is unavailable.");
  });
  const result = await service.invoke(
    "project",
    {},
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.equal(result.ok, false);
  assert.deepEqual(result.error, { code: "missing", message: "Koda engine is unavailable." });
});

test("service rejects concurrent mutations for one workspace", async () => {
  const root = await workspace();
  let release = (): void => undefined;
  const pendingRunner: JsonRunner = async () =>
    new Promise((resolve) => {
      release = (): void => resolve({});
    });
  const service = new KodaService(async () => ENGINE, pendingRunner);
  const first = service.invoke(
    "begin",
    { request: "First" },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  await new Promise((resolve) => setImmediate(resolve));
  const second = await service.invoke(
    "begin",
    { request: "Second" },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.equal(second.error?.code, "invalid_input");
  release();
  assert.equal((await first).ok, true);
});

test("enriched profile results preserve unknown and unavailable capability states", async () => {
  const root = await workspace();
  const payload = {
    schema_version: 4,
    engineering_stale: false,
    engineering_profile: { project_mode: "existing" },
    quality_contract: {
      capabilities: [
        { name: "compatibility", state: "unknown", verification: "not_run" },
        { name: "static_security", state: "unavailable", verification: "unavailable" },
      ],
    },
  };
  const service = new KodaService(async () => ENGINE, async () => payload);
  const result = await service.invoke(
    "status",
    { missionId: "mission-1" },
    { workspaceRoots: [root], timeoutSeconds: 30 },
  );
  assert.equal(result.ok, true);
  assert.deepEqual(result.data, payload);
});
