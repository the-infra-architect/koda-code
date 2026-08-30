from pathlib import Path

from koda_code.discovery import inspect_repository


def test_detects_existing_language_framework_ui_and_ci(git_repo: Path) -> None:
    (git_repo / "manage.py").write_text("", encoding="utf-8")
    (git_repo / "src" / "pages").mkdir(parents=True)
    (git_repo / "src" / "pages" / "home.tsx").write_text("export default 1", encoding="utf-8")
    (git_repo / "tests").mkdir()
    (git_repo / "tests" / "test_app.py").write_text("", encoding="utf-8")
    (git_repo / ".github" / "workflows").mkdir(parents=True)
    (git_repo / ".github" / "workflows" / "ci.yml").write_text("name: CI", encoding="utf-8")
    result = inspect_repository(git_repo)
    assert result.is_git_repository
    assert result.languages[:2] == ("Python", "TypeScript")
    assert "Django" in result.frameworks
    assert result.has_user_interface
    assert result.has_tests
    assert result.has_ci


def test_detects_data_markers_from_paths(git_repo: Path) -> None:
    (git_repo / "postgres_models.py").write_text("", encoding="utf-8")
    result = inspect_repository(git_repo)
    assert result.data_signals == ("PostgreSQL",)


def test_inspection_is_bounded(git_repo: Path) -> None:
    for index in range(5):
        (git_repo / f"file_{index}.py").write_text("", encoding="utf-8")
    result = inspect_repository(git_repo, max_files=2)
    assert result.inspected_files == 2
    assert any("stopped" in note for note in result.notes)
