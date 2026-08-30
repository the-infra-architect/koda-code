import assert from "node:assert/strict";
import { chmod, mkdir, mkdtemp, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import {
  EngineError,
  resolveEngine,
  runJson,
  runProcess,
  type CancellationLike,
  type EngineCommand,
} from "../src/engine.js";

async function nodeCommand(source: string): Promise<{ command: EngineCommand; directory: string }> {
  const directory = await mkdtemp(join(tmpdir(), "koda-engine-"));
  const script = join(directory, "engine.js");
  await writeFile(script, source, "utf8");
  return {
    command: { executable: process.execPath, prefix: [script], source: "configured", version: "0.4.0" },
    directory,
  };
}

test("process adapter returns JSON and reports engine failures", async () => {
  const success = await nodeCommand('process.stdout.write(JSON.stringify({ok:true}));');
  assert.deepEqual(
    await runJson(success.command, [], success.directory, {
      timeoutMilliseconds: 1000,
      maxOutputBytes: 1024,
    }),
    { ok: true },
  );
  const failure = await nodeCommand('process.stderr.write("safe failure"); process.exit(7);');
  await assert.rejects(
    runProcess(failure.command, [], failure.directory, {
      timeoutMilliseconds: 1000,
      maxOutputBytes: 1024,
    }),
    (error: unknown) => error instanceof EngineError && error.code === "failed",
  );
});

test("process adapter rejects malformed and oversized output", async () => {
  const malformed = await nodeCommand('process.stdout.write("not json");');
  await assert.rejects(
    runJson(malformed.command, [], malformed.directory, {
      timeoutMilliseconds: 1000,
      maxOutputBytes: 1024,
    }),
    (error: unknown) => error instanceof EngineError && error.code === "malformed_output",
  );
  const primitive = await nodeCommand("process.stdout.write('null');");
  await assert.rejects(
    runJson(primitive.command, [], primitive.directory, {
      timeoutMilliseconds: 1000,
      maxOutputBytes: 1024,
    }),
    (error: unknown) => error instanceof EngineError && error.code === "malformed_output",
  );
  const oversized = await nodeCommand('process.stdout.write("x".repeat(4096));');
  await assert.rejects(
    runProcess(oversized.command, [], oversized.directory, {
      timeoutMilliseconds: 1000,
      maxOutputBytes: 128,
    }),
    (error: unknown) => error instanceof EngineError && error.code === "output_limit",
  );
});

test("process adapter honors timeout and cancellation", async () => {
  const slow = await nodeCommand("setTimeout(() => process.stdout.write('{}'), 5000);");
  await assert.rejects(
    runProcess(slow.command, [], slow.directory, {
      timeoutMilliseconds: 20,
      maxOutputBytes: 1024,
    }),
    (error: unknown) => error instanceof EngineError && error.code === "timed_out",
  );
  let cancel = (): void => undefined;
  const token: CancellationLike = {
    isCancellationRequested: false,
    onCancellationRequested: (listener) => {
      cancel = listener;
      return { dispose: (): void => undefined };
    },
  };
  const pending = runProcess(slow.command, [], slow.directory, {
    timeoutMilliseconds: 1000,
    maxOutputBytes: 1024,
    cancellation: token,
  });
  setTimeout(cancel, 10);
  await assert.rejects(
    pending,
    (error: unknown) => error instanceof EngineError && error.code === "cancelled",
  );
});

test("resolver validates configured executables and engine versions", async () => {
  const directory = await mkdtemp(join(tmpdir(), "koda-resolver-"));
  const compatible = join(directory, "compatible");
  await writeFile(compatible, "#!/usr/bin/env node\nconsole.log('Koda-Code 0.4.2');\n", "utf8");
  await chmod(compatible, 0o755);
  assert.equal((await resolveEngine(directory, compatible)).version, "0.4.2");

  const old = join(directory, "old");
  await writeFile(old, "#!/usr/bin/env node\nconsole.log('Koda-Code 0.3.9');\n", "utf8");
  await chmod(old, 0o755);
  await assert.rejects(
    resolveEngine(directory, old),
    (error: unknown) => error instanceof EngineError && error.code === "incompatible",
  );
  await assert.rejects(
    resolveEngine(directory, join(directory, "missing")),
    (error: unknown) => error instanceof EngineError && error.code === "invalid",
  );

  const impostor = join(directory, "impostor");
  await writeFile(impostor, "#!/usr/bin/env node\nconsole.log('Not Koda');\n", "utf8");
  await chmod(impostor, 0o755);
  await assert.rejects(
    resolveEngine(directory, impostor),
    (error: unknown) => error instanceof EngineError && error.code === "invalid",
  );
});

test("resolver finds a workspace-local Koda executable", async () => {
  const directory = await mkdtemp(join(tmpdir(), "koda-local-"));
  const executable = join(directory, ".venv", "bin", "koda");
  await mkdir(join(directory, ".venv", "bin"), { recursive: true });
  await writeFile(executable, "#!/usr/bin/env node\nconsole.log('Koda-Code 0.4.1');\n", "utf8");
  await chmod(executable, 0o755);
  const resolved = await resolveEngine(directory, undefined);
  assert.equal(resolved.source, "workspace");
  assert.equal(resolved.executable, executable);
});
