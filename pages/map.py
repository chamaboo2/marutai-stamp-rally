from __future__ import annotations

import streamlit as st
from streamlit_folium import st_folium

from components.facility_card import CATEGORY_LABELS, render_facility_card
from services.map_service import build_facility_map
from services.storage_service import list_facilities, visited_facility_ids

WARDS = [
    "千代田区","中央区","港区","新宿区","文京区","台東区","墨田区","江東区","品川区","目黒区","大田区",
    "世田谷区","渋谷区","中野区","杉並区","豊島区","北区","荒川区","板橋区","練馬区","足立区","葛飾区","江戸川区",
]


def render(go):
    st.markdown("# 🗺️ 地図から探す")
    facilities = list_facilities()
    visited = visited_facility_ids()

    if not facilities:
        st.warning("施設データがまだありません。data/facilities.csv に施設を登録してください。")
        st_folium(build_facility_map([], visited), width=None, height=460, returned_objects=[])
        return

    default_open_air = st.query_params.get("open_air") == "1"
    with st.expander("絞り込み", expanded=True):
        ward = st.selectbox("区から探す", ["すべて"] + WARDS)
        c1, c2 = st.columns(2)
        open_air = c1.checkbox("露天風呂あり", value=default_open_air)
        natural = c2.checkbox("天然温泉")
        category = st.multiselect(
            "施設種類",
            options=list(CATEGORY_LABELS.keys()),
            format_func=lambda x: CATEGORY_LABELS[x],
        )
        visit_state = st.selectbox("訪問状態", ["すべて", "訪問済み", "未訪問"])

    filtered = []
    for f in facilities:
        fid = str(f.get("id"))
        if ward != "すべて" and f.get("ward") != ward:
            continue
        if open_air and not f.get("has_open_air_bath"):
            continue
        if natural and not f.get("has_natural_hot_spring"):
            continue
        if category and f.get("category") not in category:
            continue
        if visit_state == "訪問済み" and fid not in visited:
            continue
        if visit_state == "未訪問" and fid in visited:
            continue
        filtered.append(f)

    st.caption(f"{len(filtered)}施設を表示")
    m = build_facility_map(filtered, visited)
    st_folium(m, width=None, height=500, returned_objects=["last_object_clicked"])

    st.markdown("### 施設一覧")
    for f in filtered:
        render_facility_card(f, str(f.get("id")) in visited, lambda fid: go("facilities", facility_id=fid), "map")
