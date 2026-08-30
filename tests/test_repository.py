from pathlib import Path

import pytest

from koda_code.errors import KodaError
from koda_code.repository import ensure_inside, repository_root


def test_finds_git_root_from_nested_folder(git_repo: Path) -> None:
    nested = git_repo / "a" / "b"
    nested.mkdir(parents=True)
    assert repository_root(nested) == git_repo.resolve()


def test_non_git_folder_is_its_own_root(tmp_path: Path) -> None:
    assert repository_root(tmp_path) == tmp_path.resolve()


def test_missing_folder_is_actionable(tmp_path: Path) -> None:
    with pytest.raises(KodaError, match="does not exist"):
        repository_root(tmp_path / "missing")


def test_path_containment(git_repo: Path) -> None:
    inside = git_repo / "src" / "app.py"
    assert ensure_inside(git_repo, inside) == inside.resolve()
    with pytest.raises(KodaError, match="inside the project"):
        ensure_inside(git_repo, git_repo.parent / "outside.py")
