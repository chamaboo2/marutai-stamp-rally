from __future__ import annotations

import streamlit as st

from services.storage_service import list_visits, photo_path


def render(go):
    st.markdown("# 📖 スタンプ帳")
    visits = list_visits()
    if not visits:
        st.info("まだスタンプがありません。『行ってきた！』から最初の1湯を記録できます。")
        return

    sort_mode = st.segmented_control(
        "並べ替え",
        ["新しい順", "古い順", "区ごと", "施設名順"],
        default="新しい順",
        selection_mode="single",
    )

    def name(v): return (v.get("facilities") or {}).get("name", "")
    def ward(v): return (v.get("facilities") or {}).get("ward", "")
    if sort_mode == "古い順":
        visits = sorted(visits, key=lambda v: str(v.get("visited_date", "")))
    elif sort_mode == "区ごと":
        visits = sorted(visits, key=lambda v: (ward(v), str(v.get("visited_date", ""))), reverse=False)
    elif sort_mode == "施設名順":
        visits = sorted(visits, key=lambda v: (name(v), str(v.get("visited_date", ""))))
    else:
        visits = sorted(visits, key=lambda v: str(v.get("visited_date", "")), reverse=True)

    for i in range(0, len(visits), 2):
        cols = st.columns(2)
        for j, visit in enumerate(visits[i:i+2]):
            f = visit.get("facilities") or {}
            with cols[j]:
                with st.container(border=True):
                    url = photo_path(visit.get("stamped_photo_path"))
                    if url:
                        st.image(url, use_container_width=True)
                    st.markdown(f"**{f.get('name','施設名未取得')}**")
                    st.caption(f"○たい　{f.get('ward','')}　{visit.get('visited_date','')}")
                    if st.button("詳しく見る", key=f"stamp_{visit.get('id')}", use_container_width=True):
                        go("facilities", facility_id=str(visit.get("facility_id")))
