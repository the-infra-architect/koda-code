from pathlib import Path

from koda_code.security import scan_paths


def test_detects_sensitive_filename(tmp_path: Path) -> None:
    secret = tmp_path / ".env"
    secret.write_text("SAFE=example", encoding="utf-8")
    assert scan_paths(tmp_path, [secret]) == ["Sensitive filename: .env"]


def test_detects_secret_assignment(tmp_path: Path) -> None:
    source = tmp_path / "settings.py"
    field = "api" + "_key"
    value = "actually-" + "secret-value"
    source.write_text(f'{field} = "{value}"\n', encoding="utf-8")
    assert scan_paths(tmp_path, [source]) == ["Possible secret assignment in settings.py"]


def test_allows_documented_placeholder(tmp_path: Path) -> None:
    source = tmp_path / "settings.py"
    source.write_text('api_key = "placeholder"\n', encoding="utf-8")
    assert scan_paths(tmp_path, [source]) == []


def test_skips_binary_and_large_files(tmp_path: Path) -> None:
    binary = tmp_path / "image.bin"
    binary.write_bytes(b"\xff\xfe")
    large = tmp_path / "large.txt"
    large.write_text("x" * 1_000_001, encoding="utf-8")
    assert scan_paths(tmp_path, [binary, large]) == []
