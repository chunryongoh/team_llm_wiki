from __future__ import annotations

from .models import PacketType


PACKET_ROUTE_MAP = {
    PacketType.REFERENCE: "wiki/sources",
    PacketType.MEETING: "wiki/sources",
    PacketType.EXPERIMENT: "wiki/experiments",
    PacketType.FEATURE: "wiki/features",
    PacketType.MODEL: "wiki/models",
    PacketType.PERFORMANCE: "wiki/performance",
    PacketType.PREPROCESSING: "wiki/datasets",
    PacketType.AUGMENTATION: "wiki/datasets",
}


def packet_target_path(packet_type: PacketType, packet_id: str) -> str:
    return f"{PACKET_ROUTE_MAP[packet_type]}/{packet_id}.md"
