from __future__ import annotations

from typing import Any, Callable

import streamlit as st

CATEGORY_LABELS = {
    "sento": "銭湯",
    "super_sento": "スーパー銭湯",
    "spa": "日帰り温浴施設",
    "other": "その他の温浴施設",
}


def render_facility_card(
    facility: dict[str, Any],
    visited: bool,
    on_detail: Callable[[str], None],
    key_prefix: str = "facility",
) -> None:
    tags = []
    if facility.get("has_open_air_bath"):
        tags.append("♨ 露天風呂あり")
    if facility.get("has_natural_hot_spring"):
        tags.append("♨ 天然温泉")
    tags.append(CATEGORY_LABELS.get(facility.get("category"), "温浴施設"))
    state = "○たい　行ったよ！" if visited else "未訪問"

    with st.container(border=True):
        st.markdown(f"### {facility.get('name','名称未設定')}")
        st.caption(f"{facility.get('ward','')} ｜ {state}")
        st.write("　".join(tags))
        if st.button("詳しく見る", key=f"{key_prefix}_{facility.get('id')}", use_container_width=True):
            on_detail(str(facility.get("id")))
