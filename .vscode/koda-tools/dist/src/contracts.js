"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InputError = exports.FINGERPRINT = exports.MISSION_ID = exports.OUTCOMES = exports.AGENTS = void 0;
exports.recordValue = recordValue;
exports.requiredString = requiredString;
exports.optionalString = optionalString;
exports.missionId = missionId;
exports.oneOf = oneOf;
exports.optionalBoolean = optionalBoolean;
exports.evidenceFingerprint = evidenceFingerprint;
exports.AGENTS = new Set([
    "engineer",
    "ui_ux",
    "tester",
    "reviewer",
    "debugger",
]);
exports.OUTCOMES = new Set(["passed", "needs_work", "blocked"]);
exports.MISSION_ID = /^[a-z0-9-]+$/u;
exports.FINGERPRINT = /^[a-f0-9]{64}$/u;
class InputError extends Error {
    constructor(message) {
        super(message);
        this.name = "InputError";
    }
}
exports.InputError = InputError;
function recordValue(input) {
    if (typeof input !== "object" || input === null || Array.isArray(input)) {
        throw new InputError("Tool input must be a JSON object.");
    }
    return input;
}
function requiredString(input, key, maximum) {
    const value = input[key];
    if (typeof value !== "string") {
        throw new InputError(`${key} must be a string.`);
    }
    const cleaned = value.trim();
    if (cleaned.length === 0) {
        throw new InputError(`${key} must not be empty.`);
    }
    if (cleaned.length > maximum) {
        throw new InputError(`${key} must contain at most ${String(maximum)} characters.`);
    }
    if (cleaned.includes("\0")) {
        throw new InputError(`${key} contains an invalid null byte.`);
    }
    return cleaned;
}
function optionalString(input, key, maximum) {
    if (input[key] === undefined) {
        return undefined;
    }
    return requiredString(input, key, maximum);
}
function missionId(input) {
    const value = requiredString(input, "missionId", 72);
    if (!exports.MISSION_ID.test(value)) {
        throw new InputError("missionId may contain only lowercase letters, numbers, and hyphens.");
    }
    return value;
}
function oneOf(input, key, allowed) {
    const value = requiredString(input, key, 32);
    if (!allowed.has(value)) {
        throw new InputError(`${key} has an unsupported value: ${value}`);
    }
    return value;
}
function optionalBoolean(input, key) {
    const value = input[key];
    if (value === undefined) {
        return false;
    }
    if (typeof value !== "boolean") {
        throw new InputError(`${key} must be a boolean.`);
    }
    return value;
}
function evidenceFingerprint(input) {
    const value = optionalString(input, "evidenceFingerprint", 64);
    if (value !== undefined && !exports.FINGERPRINT.test(value)) {
        throw new InputError("evidenceFingerprint must be a lowercase SHA-256 value.");
    }
    return value;
}
//# sourceMappingURL=contracts.js.map