from __future__ import annotations

from typing import Any, Iterable

import folium

TOKYO_CENTER = (35.6762, 139.6503)


def build_facility_map(
    facilities: Iterable[dict[str, Any]],
    visited_ids: set[str],
    zoom_start: int = 11,
) -> folium.Map:
    m = folium.Map(
        location=TOKYO_CENTER,
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True,
        prefer_canvas=True,
    )

    for facility in facilities:
        lat, lon = facility.get("latitude"), facility.get("longitude")
        if lat in (None, "") or lon in (None, ""):
            continue
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            continue

        visited = str(facility.get("id")) in visited_ids
        if visited:
            html = """
            <div style='width:42px;height:42px;border-radius:50%;background:#d92e28;color:white;
            border:4px solid #fff7e8;box-shadow:0 2px 8px #0004;display:flex;align-items:center;
            justify-content:center;font-weight:900;font-size:16px;font-family:sans-serif;'>たい</div>
            """
        else:
            html = """
            <div style='width:34px;height:34px;border-radius:18px 18px 18px 3px;background:#103b66;
            color:white;transform:rotate(-45deg);border:3px solid #fff7e8;box-shadow:0 2px 7px #0004;
            display:flex;align-items:center;justify-content:center;'>
              <span style='transform:rotate(45deg);font-size:19px;'>♨</span>
            </div>
            """
        popup = folium.Popup(
            f"<b>{facility.get('name','')}</b><br>{facility.get('ward','')}<br>"
            + ("訪問済み" if visited else "未訪問"),
            max_width=260,
        )
        folium.Marker(
            location=[lat, lon],
            popup=popup,
            tooltip=facility.get("name", ""),
            icon=folium.DivIcon(html=html, icon_size=(42, 42), icon_anchor=(21, 36)),
        ).add_to(m)
    return m
