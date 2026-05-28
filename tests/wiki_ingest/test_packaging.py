from pathlib import Path
import tomllib


def test_test_extra_includes_schema_validator_dependency():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    test_deps = pyproject["project"]["optional-dependencies"]["test"]

    assert any(dep.lower().startswith("jsonschema") for dep in test_deps)
