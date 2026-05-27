from __future__ import annotations

import json
from typing import Any

from .models import PacketManifest, as_jsonable


def compile_packet(manifest: PacketManifest, packet_root: str, risk_tier: str) -> dict[str, Any]:
    raw_paths = manifest.raw_path_map if manifest.raw_path_map else manifest.raw_paths
    payload = {
        "id": manifest.id,
        "packet_type": manifest.type,
        "title": manifest.title,
        "date": manifest.date,
        "owner": manifest.owner,
        "status": manifest.status,
        "task": manifest.task,
        "dataset": manifest.dataset,
        "split": manifest.split,
        "model": manifest.model,
        "claim_boundary": manifest.claim_boundary,
        "claim_status": manifest.claim_status,
        "summary": manifest.summary,
        "raw_paths": raw_paths,
        "intended_wiki_targets": manifest.intended_wiki_targets,
        "metrics_to_verify": manifest.metrics_to_verify,
        "claims": manifest.claims,
        "packet_root": packet_root,
        "risk_tier": risk_tier,
    }
    compiled = as_jsonable(payload)
    json.dumps(compiled)
    return compiled
