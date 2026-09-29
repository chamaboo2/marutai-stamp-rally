from __future__ import annotations

from html import escape
from typing import Any, Callable

import streamlit as st

CATEGORY_LABELS = {
    "sento": "銭湯",
    "super_sento": "スーパー銭湯",
    "spa": "日帰り温浴施設",
    "other": "その他の温浴施設",
}


def _yn_tag(label: str, value: bool) -> str:
    css = "yes" if value else "no"
    text = f"♨ {label}あり" if value else f"{label}なし／未登録"
    return f'<span class="facility-tag {css}">{escape(text)}</span>'


def render_facility_card(
    facility: dict[str, Any],
    visited: bool,
    on_detail: Callable[[str], None],
    key_prefix: str = "facility",
) -> None:
    name = escape(str(facility.get("name", "名称未設定")))
    ward = escape(str(facility.get("ward", "")))
    category = escape(CATEGORY_LABELS.get(facility.get("category"), "温浴施設"))
    state_text = "○たい　訪問済み" if visited else "未訪問"
    status_class = "facility-status visited" if visited else "facility-status"

    st.markdown(
        f"""
        <div class="facility-card">
          <div class="facility-card-title">{name}</div>
          <div class="facility-card-meta">{ward}　｜　{category}</div>
          <div class="facility-tags">
            {_yn_tag("露天風呂", bool(facility.get("has_open_air_bath")))}
            {_yn_tag("天然温泉", bool(facility.get("has_natural_hot_spring")))}
          </div>
          <div class="{status_class}">{state_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("詳しく見る", key=f"{key_prefix}_{facility.get('id')}", use_container_width=True):
        on_detail(str(facility.get("id")))
