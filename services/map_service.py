from __future__ import annotations

from html import escape
from typing import Any, Iterable
from urllib.parse import quote

import folium

TOKYO_CENTER = (35.6764, 139.7483)
TOKYO_23_BOUNDS = [[35.52, 139.55], [35.82, 139.93]]
CATEGORY_LABELS = {
    "sento": "銭湯",
    "super_sento": "スーパー銭湯",
    "spa": "日帰り温浴施設",
    "other": "その他の温浴施設",
}


def build_facility_map(
    facilities: Iterable[dict[str, Any]],
    visited_ids: set[str],
    zoom_start: int = 11,
    fit_23_wards: bool | None = None,
) -> folium.Map:
    if fit_23_wards is None:
        fit_23_wards = zoom_start <= 12

    m = folium.Map(
        location=TOKYO_CENTER,
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True,
        prefer_canvas=True,
        min_zoom=9,
    )
    if fit_23_wards:
        m.fit_bounds(TOKYO_23_BOUNDS, padding=(8, 8))

    for facility in facilities:
        lat, lon = facility.get("latitude"), facility.get("longitude")
        if lat in (None, "") or lon in (None, ""):
            continue
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            continue

        fid = str(facility.get("id"))
        visited = fid in visited_ids
        if visited:
            marker_html = """
            <div style='width:42px;height:42px;border-radius:50%;background:#d9362b;color:white;
            border:4px solid #fff7e8;box-shadow:0 2px 8px #0003;display:flex;align-items:center;
            justify-content:center;font-weight:900;font-size:15px;font-family:sans-serif;'>たい</div>
            """
        else:
            marker_html = """
            <div style='width:36px;height:36px;border-radius:19px 19px 19px 4px;background:#173a5e;
            color:white;transform:rotate(-45deg);border:3px solid #fff7e8;box-shadow:0 2px 7px #0003;
            display:flex;align-items:center;justify-content:center;'>
              <span style='transform:rotate(45deg);font-size:19px;'>♨</span>
            </div>
            """

        name = escape(str(facility.get("name", "")))
        ward = escape(str(facility.get("ward", "")))
        category = escape(CATEGORY_LABELS.get(facility.get("category"), "温浴施設"))
        visit_text = "訪問済み" if visited else "未訪問"
        open_air = "露天風呂あり" if facility.get("has_open_air_bath") else "露天風呂なし／未登録"
        natural = "天然温泉" if facility.get("has_natural_hot_spring") else "天然温泉なし／未登録"
        detail_url = f"?page=facilities&facility_id={quote(fid, safe='')}"
        popup_html = f"""
        <div style="font-family:-apple-system,BlinkMacSystemFont,'Yu Gothic',sans-serif;color:#173a5e;min-width:190px;line-height:1.55;">
          <div style="font-size:16px;font-weight:800;margin-bottom:3px;">{name}</div>
          <div style="font-size:13px;">{ward}<br>施設種別：{category}</div>
          <div style="font-size:13px;font-weight:700;color:{'#d9362b' if visited else '#173a5e'};">{visit_text}</div>
          <div style="font-size:12px;margin-top:5px;">♨ {escape(open_air)}<br>♨ {escape(natural)}</div>
          <a href="{detail_url}" target="_top" style="display:block;margin-top:8px;padding:7px 10px;border-radius:9px;background:#d9362b;color:#fff;text-align:center;text-decoration:none;font-weight:800;font-size:13px;">詳しく見る</a>
        </div>
        """
        popup = folium.Popup(popup_html, max_width=280)
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=name,
            icon=folium.DivIcon(html=marker_html, icon_size=(42, 42), icon_anchor=(21, 36)),
        ).add_to(m)
    return m
