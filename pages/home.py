from __future__ import annotations

from collections import Counter

import streamlit as st

from components.stamp import render_logo
from services.storage_service import list_visits


def render(go):
    render_logo()
    st.markdown("<div class='hero-question'>今日はどこのお風呂へ行く？</div>", unsafe_allow_html=True)

    if st.button("🗺️  地図から探す", key="home_map", type="primary", use_container_width=True):
        go("map")
    if st.button("♨  露天風呂を探す", key="home_open_air", use_container_width=True):
        go("map", open_air="1")
    if st.button("📖  スタンプ帳", key="home_stampbook", use_container_width=True):
        go("stampbook")
    if st.button("📷  行ってきた！", key="home_visit", use_container_width=True):
        go("visit")

    visits = list_visits()
    unique_facilities = {str(v.get("facility_id")) for v in visits}
    total = len(unique_facilities)
    st.markdown(
        f"<div class='count-card'><span>これまでに</span><strong>{total}湯！</strong></div>",
        unsafe_allow_html=True,
    )

    if visits:
        unique_by_facility = {}
        for v in visits:
            unique_by_facility.setdefault(str(v.get("facility_id")), v.get("facilities") or {})
        ward_counter = Counter(f.get("ward", "") for f in unique_by_facility.values())
        ward_counter.pop("", None)
        if ward_counter:
            st.markdown("#### 区ごとの記録")
            cols = st.columns(min(3, len(ward_counter)))
            for i, (ward, count) in enumerate(ward_counter.most_common(6)):
                cols[i % len(cols)].metric(ward, f"{count}湯")

        achieved = [n for n in (3, 5, 10, 20) if total >= n]
        if achieved:
            st.success(f"{max(achieved)}湯達成！")
