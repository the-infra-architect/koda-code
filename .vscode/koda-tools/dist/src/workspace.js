"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.selectWorkspace = selectWorkspace;
const promises_1 = require("node:fs/promises");
const node_path_1 = require("node:path");
const contracts_js_1 = require("./contracts.js");
function isContained(root, candidate) {
    const segment = (0, node_path_1.relative)(root, candidate);
    return segment === "" || (!segment.startsWith("..") && !(0, node_path_1.isAbsolute)(segment));
}
async function selectWorkspace(workspaceRoots, requested) {
    if (workspaceRoots.length === 0) {
        throw new contracts_js_1.InputError("Open a workspace folder before using Koda.");
    }
    const canonicalRoots = await Promise.all(workspaceRoots.map(async (root) => (0, promises_1.realpath)(root)));
    if (requested === undefined) {
        if (canonicalRoots.length !== 1) {
            throw new contracts_js_1.InputError("Multiple workspace folders are open. Supply repository to select one explicitly.");
        }
        return canonicalRoots[0];
    }
    if (requested.length > 4096 || requested.includes("\0")) {
        throw new contracts_js_1.InputError("repository is invalid or too long.");
    }
    const bases = (0, node_path_1.isAbsolute)(requested)
        ? [requested]
        : canonicalRoots.map((root) => (0, node_path_1.resolve)(root, requested));
    const matches = [];
    for (const candidate of bases) {
        let canonical;
        try {
            canonical = await (0, promises_1.realpath)(candidate);
        }
        catch {
            continue;
        }
        if (canonicalRoots.some((root) => isContained(root, canonical))) {
            matches.push(canonical);
        }
    }
    const unique = [...new Set(matches)];
    if (unique.length === 1)
        return unique[0];
    if (unique.length > 1) {
        throw new contracts_js_1.InputError("repository matches multiple workspace folders; supply an absolute path.");
    }
    throw new contracts_js_1.InputError("repository must be an existing path inside an open workspace folder.");
}
//# sourceMappingURL=workspace.js.map