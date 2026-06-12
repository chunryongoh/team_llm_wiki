import json

from team_llm_wiki.wiki_ingest.compile import compile_packet
from team_llm_wiki.wiki_ingest.models import Claim, MetricCheck, PacketManifest, PacketType


def test_compile_packet_normalizes_lineage_and_is_json_serializable():
    manifest = PacketManifest(
        id="exp-1",
        type=PacketType.EXPERIMENT,
        title="Experiment One",
        date="2026-05-27",
        owner="alice",
        status="submitted",
        task="classification",
        dataset={"name": "benchmark-set", "version": "v1"},
        split={"name": "dev", "group_key": "patient_id"},
        model={"family": "llama", "weights_in_repo": False},
        claim_boundary="Only applies to dev split.",
        claim_status="tentative",
        summary="Run summary.",
        raw_paths={"metrics": "result.json"},
        intended_wiki_targets=["wiki/reports/exp-1.md"],
        metrics_to_verify=[MetricCheck(raw_path="result.json", metric_key="accuracy", reported_value=0.82)],
        claims=[Claim(status="supported", text="Accuracy improved.")],
    )

    payload = compile_packet(
        manifest,
        packet_root="raw/users/alice/exp-1",
        risk_tier="tier3-performance",
        publish_action="bot_pr",
    )

    assert payload == {
        "id": "exp-1",
        "packet_type": "experiment",
        "title": "Experiment One",
        "date": "2026-05-27",
        "owner": "alice",
        "status": "submitted",
        "task": "classification",
        "dataset": {"name": "benchmark-set", "version": "v1", "hash": None},
        "split": {"name": "dev", "group_key": "patient_id", "fold_file": None},
        "model": {"family": "llama", "weights_in_repo": False},
        "claim_boundary": "Only applies to dev split.",
        "claim_status": "tentative",
        "summary": "Run summary.",
        "raw_paths": {"metrics": "result.json"},
        "intended_wiki_targets": ["wiki/reports/exp-1.md"],
        "metrics_to_verify": [
            {
                "raw_path": "result.json",
                "metric_key": "accuracy",
                "reported_value": 0.82,
                "tolerance": 0.0,
                "name": None,
                "key": None,
                "expected": None,
                "actual": None,
            }
        ],
        "claims": [{"status": "supported", "text": "Accuracy improved."}],
        "packet_root": "raw/users/alice/exp-1",
        "risk_tier": "tier3-performance",
        "publish_action": "bot_pr",
    }
    json.dumps(payload, sort_keys=True)


def test_compile_packet_preserves_unlabeled_raw_paths_as_list():
    manifest = PacketManifest(
        id="exp-2",
        type=PacketType.EXPERIMENT,
        title="Experiment Two",
        date="2026-05-27",
        owner="alice",
        status="submitted",
        task="classification",
        dataset={"name": "benchmark-set", "version": "v1"},
        split={"name": "dev"},
        model={"family": "llama"},
        claim_boundary="Only applies to dev split.",
        claim_status="tentative",
        summary="Run summary.",
        raw_paths=["result.json", "folds.csv"],
        intended_wiki_targets=["wiki/reports/exp-2.md"],
    )

    payload = compile_packet(manifest, packet_root="raw/users/alice/exp-2", risk_tier="tier3-performance")

    assert payload["raw_paths"] == ["result.json", "folds.csv"]
    json.dumps(payload, sort_keys=True)
