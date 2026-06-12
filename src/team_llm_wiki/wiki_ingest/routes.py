from __future__ import annotations

from pathlib import Path

from .models import PacketType
from .models import _validate_kebab_id
from .route_contract import load_route_contract


PACKET_ROUTE_MAP = {
    PacketType.REFERENCE: "wiki/reports",
    PacketType.MEETING: "wiki/reports",
    PacketType.EXPERIMENT: "wiki/reports",
    PacketType.FEATURE: "wiki/features",
    PacketType.MODEL: "wiki/models",
    PacketType.PERFORMANCE: "wiki/performance",
    PacketType.PREPROCESSING: "wiki/preprocessing",
    PacketType.AUGMENTATION: "wiki/preprocessing",
    PacketType.DATASET: "wiki/preprocessing",
    PacketType.BENCHMARK: "wiki/performance",
}


def packet_route(packet_type: PacketType, *, repo_root: Path | None = None) -> str:
    if repo_root is None:
        return PACKET_ROUTE_MAP[packet_type]
    contract = load_route_contract(repo_root or Path("."))
    return contract.packet_route(packet_type)


def packet_target_path(packet_type: PacketType, packet_id: str, *, repo_root: Path | None = None) -> str:
    _validate_kebab_id(packet_id)
    return f"{packet_route(packet_type, repo_root=repo_root)}/{packet_id}.md"
