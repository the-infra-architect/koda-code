from koda_code.approach import choose_approach
from koda_code.models import RepositoryEvidence, RequirementUnderstanding


def repo(
    *, languages: tuple[str, ...] = (), frameworks: tuple[str, ...] = ()
) -> RepositoryEvidence:
    return RepositoryEvidence("/p", True, languages, frameworks, True, True, False, (), 10)


def understanding(
    *,
    constraints: tuple[str, ...] = (),
    questions: tuple[str, ...] = (),
    signals: tuple[str, ...] = (),
) -> RequirementUnderstanding:
    return RequirementUnderstanding("Build it", constraints, questions, signals)


def test_existing_project_conventions_win_over_generic_selection() -> None:
    result = choose_approach(understanding(), repo(languages=("Python",), frameworks=("Django",)))
    assert "existing project conventions" in result.summary
    assert "Django" in result.summary


def test_explicit_constraints_are_honored() -> None:
    result = choose_approach(understanding(constraints=("Rust",)), repo())
    assert "Rust" in result.summary
    assert result.constraints_honored == ("Rust",)


def test_missing_product_answers_defer_infrastructure() -> None:
    result = choose_approach(understanding(questions=("Where?",)), repo())
    assert "before selecting irreversible infrastructure" in result.summary
    assert result.decisions_deferred


def test_complexity_drivers_follow_actual_signals() -> None:
    result = choose_approach(
        understanding(signals=("sensitive_data", "scale_or_concurrency", "persistent_data")), repo()
    )
    joined = " ".join(result.complexity_drivers)
    assert "Sensitive" in joined
    assert "concurrency" in joined
    assert "Persistence" in joined


def test_unjustified_distributed_components_are_rejected() -> None:
    result = choose_approach(understanding(), repo())
    assert any("microservices" in item for item in result.complexity_avoided)
    assert any("database chosen by category" in item for item in result.complexity_avoided)
