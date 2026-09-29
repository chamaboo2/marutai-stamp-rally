from __future__ import annotations

from datetime import date
from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps

from services.stamp_service import add_visit_stamp
from services.storage_service import create_visit, list_facilities


def _normalize_photo(raw: bytes) -> bytes:
    image = Image.open(BytesIO(raw))
    image = ImageOps.exif_transpose(image).convert("RGB")
    out = BytesIO()
    image.save(out, "JPEG", quality=94, optimize=True)
    return out.getvalue()


def render(go):
    st.markdown("# 📷 行ってきた！")
    facilities = list_facilities()
    if not facilities:
        st.warning("先に施設データを登録してください。")
        return

    preselected = st.query_params.get("facility_id", "")
    labels = {str(f.get("id")): f"{f.get('name')}（{f.get('ward')}）" for f in facilities}
    ids = list(labels)
    initial = ids.index(preselected) if preselected in ids else 0

    st.markdown("### 1　訪問した施設を選ぶ")
    facility_id = st.selectbox(
        "施設",
        ids,
        index=initial,
        format_func=lambda x: labels[x],
        label_visibility="collapsed",
    )

    st.markdown("### 2　写真を撮影／選択")
    mode = st.radio("写真の追加方法", ["カメラで撮る", "写真を選ぶ"], horizontal=False)
    uploaded = (
        st.camera_input("銭湯・施設前で1枚", label_visibility="collapsed")
        if mode == "カメラで撮る"
        else st.file_uploader(
            "写真を選ぶ",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
        )
    )

    st.markdown("### 3　訪問日")
    visited_date = st.date_input("訪問日", value=date.today(), label_visibility="collapsed")

    st.markdown("### 4　スタンプを押す")
    if st.button("○たい　スタンプを押す！", type="primary", use_container_width=True):
        if uploaded is None:
            st.warning("銭湯前の写真を1枚追加してね")
            return
        try:
            original = _normalize_photo(uploaded.getvalue())
            stamped = add_visit_stamp(original, visited_date.isoformat(), position="bottom_right")
            create_visit(facility_id, visited_date.isoformat(), original, stamped)
            st.session_state["last_stamped_photo"] = stamped
            st.session_state["last_visit_facility"] = labels[facility_id]
            st.success("たい！またひとつ増えたよ！")
        except Exception as exc:
            st.error("訪問記録を保存できませんでした。写真を確認して、もう一度お試しください。")
            st.caption(f"エラー: {type(exc).__name__}: {exc}")

    if st.session_state.get("last_stamped_photo"):
        st.image(
            st.session_state["last_stamped_photo"],
            caption=st.session_state.get("last_visit_facility", ""),
            use_container_width=True,
        )
        if st.button("スタンプ帳を見る", use_container_width=True):
            go("stampbook")
