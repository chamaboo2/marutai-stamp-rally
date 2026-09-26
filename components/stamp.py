from pathlib import Path

import streamlit as st

ASSET_DIR = Path(__file__).resolve().parents[1] / "assets"


def render_logo(width: int = 310) -> None:
    logo = ASSET_DIR / "logo.png"
    if logo.exists():
        st.image(str(logo), width=width)
    else:
        st.markdown(
            "<div class='brand-fallback'><span class='brand-stamp'>たい</span>"
            "<div><div class='brand-title'>まるたい<br>スタンプラリー</div>"
            "<div class='brand-sub'>東京23区のおふろめぐり</div></div></div>",
            unsafe_allow_html=True,
        )
