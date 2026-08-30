import assert from "node:assert/strict";
import { mkdir, mkdtemp, realpath, symlink } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

import { InputError } from "../src/contracts.js";
import { selectWorkspace } from "../src/workspace.js";

test("workspace selection rejects no folder and ambiguous multi-root input", async () => {
  await assert.rejects(selectWorkspace([], undefined), InputError);
  const temporary = await mkdtemp(join(tmpdir(), "koda-workspace-"));
  const first = join(temporary, "first");
  const second = join(temporary, "second");
  await mkdir(first);
  await mkdir(second);
  await assert.rejects(selectWorkspace([first, second], undefined), /Multiple workspace folders/u);
  await assert.rejects(selectWorkspace([first, second], "."), /multiple workspace folders/u);
  assert.equal(await selectWorkspace([first, second], second), await realpath(second));
});

test("workspace selection accepts nested repositories and rejects symlink escapes", async () => {
  const temporary = await mkdtemp(join(tmpdir(), "koda-workspace-"));
  const root = join(temporary, "root");
  const nested = join(root, "packages", "service");
  const outside = join(temporary, "outside");
  await mkdir(nested, { recursive: true });
  await mkdir(outside);
  assert.equal(await selectWorkspace([root], nested), await realpath(nested));
  const link = join(root, "escape");
  await symlink(outside, link);
  await assert.rejects(selectWorkspace([root], link), /inside an open workspace/u);
});
