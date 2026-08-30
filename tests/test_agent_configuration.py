from __future__ import annotations

import ast
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).parents[1]
AGENT_ROOT = REPOSITORY_ROOT / ".vscode" / "koda-tools" / "agents"
GITHUB_AGENT_ROOT = REPOSITORY_ROOT / ".github" / "agents"
SPECIALISTS = {
    "engineer.agent.md": "Engineer",
    "ui-ux.agent.md": "UI UX",
    "tester.agent.md": "Tester",
    "reviewer.agent.md": "Reviewer",
    "debugger.agent.md": "Debugger",
}
KODA_TOOLS = {
    "koda-code_project",
    "koda-code_begin",
    "koda-code_answer",
    "koda-code_status",
    "koda-code_evidence",
    "koda-code_record",
    "koda-code_check",
}


def _frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    _, block, _ = text.split("---", maxsplit=2)
    parsed: dict[str, object] = {}
    for line in block.strip().splitlines():
        key, value = line.split(":", maxsplit=1)
        cleaned = value.strip()
        if cleaned.startswith("["):
            parsed[key] = ast.literal_eval(cleaned)
        elif cleaned in {"true", "false"}:
            parsed[key] = cleaned == "true"
        else:
            parsed[key] = cleaned
    return parsed


def test_koda_is_the_only_user_visible_manager_with_exact_subagents() -> None:
    metadata = _frontmatter(AGENT_ROOT / "koda.agent.md")
    assert metadata["name"] == "Koda"
    assert metadata["target"] == "vscode"
    assert metadata["user-invocable"] is True
    assert metadata["disable-model-invocation"] is True
    assert metadata["agents"] == ["Engineer", "UI UX", "Tester", "Reviewer", "Debugger"]
    tools = set(metadata["tools"])  # type: ignore[arg-type]
    assert "agent" in tools
    assert tools >= KODA_TOOLS
    assert "infer" not in metadata
    instructions = (AGENT_ROOT / "koda.agent.md").read_text(encoding="utf-8")
    assert "Never launch parallel subagents" in instructions
    assert "UI UX** only when" in instructions
    assert "Debugger** only when" in instructions
    assert "do not impersonate" in instructions


def test_workspace_agent_mirrors_match_the_repo_local_runtime() -> None:
    runtime_files = {path.name for path in AGENT_ROOT.glob("*.agent.md")}
    github_files = {path.name for path in GITHUB_AGENT_ROOT.glob("*.agent.md")}
    assert runtime_files == github_files == {"koda.agent.md", *SPECIALISTS}
    for filename in runtime_files:
        assert (AGENT_ROOT / filename).read_text(encoding="utf-8") == (
            GITHUB_AGENT_ROOT / filename
        ).read_text(encoding="utf-8")


def test_specialists_are_hidden_and_cannot_be_selected_implicitly() -> None:
    for filename, name in SPECIALISTS.items():
        metadata = _frontmatter(AGENT_ROOT / filename)
        assert metadata["name"] == name
        assert metadata["user-invocable"] is False
        assert metadata["disable-model-invocation"] is True
        assert "infer" not in metadata


def test_reviewer_and_debugger_are_read_only_by_tool_scope() -> None:
    for filename in ("reviewer.agent.md", "debugger.agent.md"):
        tools = set(_frontmatter(AGENT_ROOT / filename)["tools"])  # type: ignore[arg-type]
        assert "edit" not in tools
        assert "execute" not in tools


def test_mutating_specialists_retain_only_normal_workspace_tools() -> None:
    for filename in ("engineer.agent.md", "ui-ux.agent.md", "tester.agent.md"):
        tools = set(_frontmatter(AGENT_ROOT / filename)["tools"])  # type: ignore[arg-type]
        assert tools == {
            "read",
            "search",
            "edit",
            "execute",
            "koda-code_status",
            "koda-code_evidence",
        }
        assert tools.isdisjoint(KODA_TOOLS - {"koda-code_status", "koda-code_evidence"})
