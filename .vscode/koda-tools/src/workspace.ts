import { realpath } from "node:fs/promises";
import { isAbsolute, relative, resolve } from "node:path";

import { InputError } from "./contracts.js";

function isContained(root: string, candidate: string): boolean {
  const segment = relative(root, candidate);
  return segment === "" || (!segment.startsWith("..") && !isAbsolute(segment));
}

export async function selectWorkspace(
  workspaceRoots: readonly string[],
  requested: string | undefined,
): Promise<string> {
  if (workspaceRoots.length === 0) {
    throw new InputError("Open a workspace folder before using Koda.");
  }
  const canonicalRoots = await Promise.all(workspaceRoots.map(async (root) => realpath(root)));
  if (requested === undefined) {
    if (canonicalRoots.length !== 1) {
      throw new InputError(
        "Multiple workspace folders are open. Supply repository to select one explicitly.",
      );
    }
    return canonicalRoots[0] as string;
  }
  if (requested.length > 4096 || requested.includes("\0")) {
    throw new InputError("repository is invalid or too long.");
  }
  const bases = isAbsolute(requested)
    ? [requested]
    : canonicalRoots.map((root) => resolve(root, requested));
  const matches: string[] = [];
  for (const candidate of bases) {
    let canonical: string;
    try {
      canonical = await realpath(candidate);
    } catch {
      continue;
    }
    if (canonicalRoots.some((root) => isContained(root, canonical))) {
      matches.push(canonical);
    }
  }
  const unique = [...new Set(matches)];
  if (unique.length === 1) return unique[0] as string;
  if (unique.length > 1) {
    throw new InputError("repository matches multiple workspace folders; supply an absolute path.");
  }
  throw new InputError("repository must be an existing path inside an open workspace folder.");
}
