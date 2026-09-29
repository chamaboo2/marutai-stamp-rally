from __future__ import annotations

from html import escape

import streamlit as st
from streamlit_folium import st_folium

from components.facility_card import CATEGORY_LABELS, render_facility_card
from services.map_service import build_facility_map
from services.storage_service import (
    get_facility,
    list_facilities,
    photo_path,
    visited_facility_ids,
    visits_for_facility,
)


def _detail(go, facility_id: str):
    f = get_facility(facility_id)
    if not f:
        st.error("施設情報が見つかりません。")
        if st.button("施設一覧へ戻る"):
            go("facilities")
        return

    visits = visits_for_facility(facility_id)
    name = escape(str(f.get("name", "")))
    ward = escape(str(f.get("ward", "")))
    category = escape(CATEGORY_LABELS.get(f.get("category"), "温浴施設"))
    address = escape(str(f.get("address", "")))
    status = "○たい　訪問済み" if visits else "未訪問"
    open_air = "♨ 露天風呂あり" if f.get("has_open_air_bath") else "露天風呂なし／未登録"
    natural = "♨ 天然温泉" if f.get("has_natural_hot_spring") else "天然温泉なし／未登録"

    st.markdown(f"# {name}")
    st.markdown(
        f"""
        <div class="detail-summary">
          <strong>{ward}</strong>　｜　{category}<br>
          {address}<br>
          <strong>{status}</strong><br>
          {escape(open_air)}　｜　{escape(natural)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if f.get("latitude") not in (None, "") and f.get("longitude") not in (None, ""):
        st_folium(
            build_facility_map([f], {facility_id} if visits else set(), zoom_start=15, fit_23_wards=False),
            width=None,
            height=300,
            returned_objects=[],
        )
    else:
        st.info("緯度・経度が未登録のため地図は表示できません。")

    if f.get("website_url"):
        st.link_button("公式サイト", str(f.get("website_url")), use_container_width=True)

    if st.button("📷 この施設で『行ってきた！』", type="primary", use_container_width=True):
        go("visit", facility_id=facility_id)

    st.markdown("### 訪問記録")
    if not visits:
        st.caption("まだ訪問記録はありません。")
    else:
        st.write(f"これまで **{len(visits)}回** 行ったよ")
        visits = sorted(visits, key=lambda v: str(v.get("visited_date", "")))
        for idx, visit in enumerate(visits, start=1):
            st.markdown(f"**{idx}回目**　{visit.get('visited_date','')}")
            url = photo_path(visit.get("stamped_photo_path"))
            if url:
                st.image(url, use_container_width=True)


def render(go):
    facility_id = st.query_params.get("facility_id")
    if facility_id:
        _detail(go, facility_id)
        return

    st.markdown("# お風呂を探す")
    st.caption("施設名や区名から、行きたいお風呂を探せます。")
    facilities = list_facilities()
    visited = visited_facility_ids()
    query = st.text_input(
        "施設名・住所から検索",
        placeholder="例：品川、新生湯",
        label_visibility="collapsed",
    )
    if query:
        q = query.strip().lower()
        facilities = [
            f for f in facilities
            if q in str(f.get("name", "")).lower()
            or q in str(f.get("address", "")).lower()
            or q in str(f.get("ward", "")).lower()
        ]

    st.caption(f"{len(facilities)}施設")
    for f in facilities:
        render_facility_card(
            f,
            str(f.get("id")) in visited,
            lambda fid: go("facilities", facility_id=fid),
            "list",
        )
    if not facilities:
        st.info("条件に合う施設はありません。")
