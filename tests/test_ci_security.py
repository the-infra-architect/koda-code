from pathlib import Path

from koda_code.ci_security import inspect_github_actions
from koda_code.models import EnforcementLevel


def _workflow(repository: Path, content: str) -> None:
    folder = repository / ".github" / "workflows"
    folder.mkdir(parents=True)
    (folder / "ci.yml").write_text(content, encoding="utf-8")


def test_github_actions_reports_least_privilege_and_safe_oidc_scope(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        """name: CI
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@0123456789012345678901234567890123456789
      - run: python -m pytest
""",
    )
    report = inspect_github_actions(tmp_path)
    assert report.least_privilege_declared
    assert report.findings == ()


def test_github_actions_detects_untrusted_shell_secret_and_permissions(
    tmp_path: Path,
) -> None:
    _workflow(
        tmp_path,
        """name: Unsafe
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo '${{ github.event.pull_request.title }}'
      - run: echo '${{ secrets.DEPLOY_TOKEN }}'
""",
    )
    report = inspect_github_actions(tmp_path)
    codes = {item.code for item in report.findings}
    assert not report.least_privilege_declared
    assert {
        "permissions_not_least_privilege",
        "untrusted_expression_in_run",
        "secret_in_executable_output",
    } <= codes
    injection = next(item for item in report.findings if item.code == "untrusted_expression_in_run")
    assert injection.enforcement is EnforcementLevel.HARD_INVARIANT


def test_third_party_action_pinning_follows_project_policy(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        """name: CI
on: [push]
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: vendor/tool@v2
""",
    )
    advisory = inspect_github_actions(tmp_path)
    finding = next(
        item for item in advisory.findings if item.code == "mutable_third_party_action_reference"
    )
    assert finding.enforcement is EnforcementLevel.RECOMMENDATION

    policy = inspect_github_actions(tmp_path, immutable_third_party_actions_required=True)
    finding = next(
        item for item in policy.findings if item.code == "mutable_third_party_action_reference"
    )
    assert finding.enforcement is EnforcementLevel.PROJECT_POLICY


def test_oidc_is_not_required_without_cloud_auth(tmp_path: Path) -> None:
    _workflow(
        tmp_path,
        """name: CI
on: [push]
permissions:
  contents: read
  id-token: write
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: python -m pytest
""",
    )
    report = inspect_github_actions(tmp_path)
    finding = next(item for item in report.findings if item.code == "oidc_without_cloud_auth")
    assert finding.enforcement is EnforcementLevel.REVIEWER_SIGNAL
