export type KodaOperation =
  | "project"
  | "begin"
  | "answer"
  | "status"
  | "evidence"
  | "record"
  | "check";

export type AgentName = "engineer" | "ui_ux" | "tester" | "reviewer" | "debugger";
export type Outcome = "passed" | "needs_work" | "blocked";

export const AGENTS = new Set<AgentName>([
  "engineer",
  "ui_ux",
  "tester",
  "reviewer",
  "debugger",
]);
export const OUTCOMES = new Set<Outcome>(["passed", "needs_work", "blocked"]);
export const MISSION_ID = /^[a-z0-9-]+$/u;
export const FINGERPRINT = /^[a-f0-9]{64}$/u;

export class InputError extends Error {
  public constructor(message: string) {
    super(message);
    this.name = "InputError";
  }
}

export function recordValue(input: unknown): Record<string, unknown> {
  if (typeof input !== "object" || input === null || Array.isArray(input)) {
    throw new InputError("Tool input must be a JSON object.");
  }
  return input as Record<string, unknown>;
}

export function requiredString(
  input: Record<string, unknown>,
  key: string,
  maximum: number,
): string {
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

export function optionalString(
  input: Record<string, unknown>,
  key: string,
  maximum: number,
): string | undefined {
  if (input[key] === undefined) {
    return undefined;
  }
  return requiredString(input, key, maximum);
}

export function missionId(input: Record<string, unknown>): string {
  const value = requiredString(input, "missionId", 72);
  if (!MISSION_ID.test(value)) {
    throw new InputError("missionId may contain only lowercase letters, numbers, and hyphens.");
  }
  return value;
}

export function oneOf<T extends string>(
  input: Record<string, unknown>,
  key: string,
  allowed: ReadonlySet<T>,
): T {
  const value = requiredString(input, key, 32);
  if (!allowed.has(value as T)) {
    throw new InputError(`${key} has an unsupported value: ${value}`);
  }
  return value as T;
}

export function optionalBoolean(input: Record<string, unknown>, key: string): boolean {
  const value = input[key];
  if (value === undefined) {
    return false;
  }
  if (typeof value !== "boolean") {
    throw new InputError(`${key} must be a boolean.`);
  }
  return value;
}

export function evidenceFingerprint(input: Record<string, unknown>): string | undefined {
  const value = optionalString(input, "evidenceFingerprint", 64);
  if (value !== undefined && !FINGERPRINT.test(value)) {
    throw new InputError("evidenceFingerprint must be a lowercase SHA-256 value.");
  }
  return value;
}
