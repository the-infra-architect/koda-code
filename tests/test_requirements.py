from koda_code.models import RepositoryEvidence
from koda_code.requirements import understand_request


def evidence(**overrides: object) -> RepositoryEvidence:
    values: dict[str, object] = {
        "root": "/project",
        "is_git_repository": True,
        "languages": (),
        "frameworks": (),
        "has_tests": False,
        "has_ci": False,
        "has_user_interface": False,
        "data_signals": (),
        "inspected_files": 0,
        "notes": (),
    }
    values.update(overrides)
    return RepositoryEvidence(**values)  # type: ignore[arg-type]


def test_beginner_inventory_request_asks_product_language_questions() -> None:
    result = understand_request("Build an inventory tracking page", evidence())
    assert "persistent_data" in result.capability_signals
    assert "user_interface" in result.capability_signals
    assert any("shared information live" in item for item in result.product_questions)
    assert any("Who needs to use this" in item for item in result.product_questions)
    assert not any("PostgreSQL" in item for item in result.product_questions)


def test_explicit_technology_constraints_are_preserved() -> None:
    result = understand_request("Use React and FastAPI with PostgreSQL", evidence())
    assert result.explicit_technical_constraints == ("React", "FastAPI", "PostgreSQL")


def test_existing_data_signal_avoids_reasking_storage_question() -> None:
    result = understand_request("Track inventory records", evidence(data_signals=("PostgreSQL",)))
    assert not any("shared information live" in item for item in result.product_questions)


def test_sensitive_request_asks_about_harm_not_security_jargon() -> None:
    result = understand_request("Store private medical notes", evidence())
    assert "sensitive_data" in result.capability_signals
    assert any("especially harmful" in item for item in result.product_questions)


def test_short_request_asks_for_outcome() -> None:
    result = understand_request("Fix it", evidence())
    assert any(
        "What should someone be able to accomplish" in question
        for question in result.product_questions
    )
