from __future__ import annotations

from glb_forge.scenes import create_thap_rua_ho_guom
from glb_forge.sites.models import HeritageSite, Province


HA_NOI = Province(
    code="29",
    slug="ha-noi",
    name="Hà Nội",
    output_name="ha_noi",
)


THAP_RUA_HO_GUOM = HeritageSite(
    site_id="thap-rua-ho-guom",
    name="Tháp Rùa - Hồ Gươm",
    province=HA_NOI,
    output_name="thap_rua_ho_guom",
    create_scene=lambda: create_thap_rua_ho_guom(seed=42),
)


HA_NOI_SITES = [
    THAP_RUA_HO_GUOM,
]


__all__ = [
    "HA_NOI",
    "HA_NOI_SITES",
    "THAP_RUA_HO_GUOM",
]
