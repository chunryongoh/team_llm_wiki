from pathlib import Path

import pytest
import yaml

from team_llm_wiki.wiki_ingest.models import IngestFailure, PacketType
from team_llm_wiki.wiki_ingest.route_contract import DEFAULT_CONTRACT_PATH, load_route_contract


def test_load_default_route_contract_exposes_canonical_routes():
    contract = load_route_contract(Path("."))

    assert contract.version == 1
    assert contract.packet_route(PacketType.DATASET) == "wiki/preprocessing"
    assert contract.packet_route(PacketType.BENCHMARK) == "wiki/performance"
    assert contract.packet_route(PacketType.EXPERIMENT) == "wiki/reports"
    assert contract.packet_route(PacketType.REFERENCE) == "wiki/reports"
    assert contract.packet_route(PacketType.MEETING) == "wiki/reports"
    assert contract.is_canonical_path("wiki/performance/dacon-leaderboard-history.md")
    assert not contract.is_canonical_path("wiki/questions/sleep-lifelog-open-questions.md")


def test_deprecated_namespace_metadata_is_complete():
    contract = load_route_contract(Path("."))

    datasets = contract.deprecated_namespace_for_path("wiki/datasets/sleep-lifelog-2024.md")
    assert datasets is not None
    assert datasets.name == "datasets"
    assert datasets.path == "wiki/datasets"
    assert datasets.replacement == "wiki/preprocessing"
    assert datasets.allowed_mode == "tombstone_only"

    briefs = contract.deprecated_namespace_for_path("wiki/briefs/latest.md")
    assert briefs is not None
    assert briefs.allowed_mode == "generated_compatibility_only"


def test_safe_synthesis_paths_reject_deprecated_namespaces_outside_migration_mode():
    contract = load_route_contract(Path("."))

    assert contract.is_allowed_synthesis_path("wiki/features/app-context-windows.md")
    assert not contract.is_allowed_synthesis_path("wiki/questions/sleep-lifelog-open-questions.md")
    assert contract.is_allowed_synthesis_path(
        "wiki/questions/sleep-lifelog-open-questions.md",
        migration_mode=True,
    )


def test_contract_load_fails_closed_for_missing_file(tmp_path):
    with pytest.raises(IngestFailure) as exc:
        load_route_contract(tmp_path)

    assert exc.value.code.value == "policy_missing"
    assert str(DEFAULT_CONTRACT_PATH) in exc.value.message


def test_contract_load_fails_closed_for_bad_packet_route(tmp_path):
    contract_path = tmp_path / DEFAULT_CONTRACT_PATH
    contract_path.parent.mkdir(parents=True)
    data = yaml.safe_load(Path(DEFAULT_CONTRACT_PATH).read_text(encoding="utf-8"))
    data["packet_routes"].pop("dataset")
    contract_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(IngestFailure) as exc:
        load_route_contract(tmp_path)

    assert exc.value.code.value == "policy_conflict"
    assert "missing packet route: dataset" in exc.value.message


def test_tombstone_validator_accepts_only_compatibility_body():
    contract = load_route_contract(Path("."))
    text = """---
page_role: compatibility
status: deprecated
canonical_target: wiki/preprocessing/sleep-lifelog-2024.md
---
# Deprecated Compatibility Page

This page has moved to [[preprocessing/sleep-lifelog-2024]].

Do not add new substantive content here. This file exists to preserve historical links and provenance.
"""

    assert contract.validate_tombstone("wiki/datasets/sleep-lifelog-2024.md", text) == []


def test_tombstone_validator_rejects_substantive_sections():
    contract = load_route_contract(Path("."))
    text = """---
page_role: compatibility
status: deprecated
canonical_target: wiki/preprocessing/sleep-lifelog-2024.md
---
# Deprecated Compatibility Page

## Metrics

- public_lb: 0.5917
"""

    errors = contract.validate_tombstone("wiki/datasets/sleep-lifelog-2024.md", text)
    assert any(error.code == "deprecated_tombstone_substantive_content" for error in errors)
