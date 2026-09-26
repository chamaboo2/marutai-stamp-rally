from __future__ import annotations

import streamlit as st

from pages import facilities, home, map as map_page, stampbook, visit

st.set_page_config(
    page_title="まるたいスタンプラリー",
    page_icon="♨️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSS = r"""
<style>
:root {
  --marutai-red:#d92e28;
  --marutai-navy:#103b66;
  --marutai-cream:#fff9ec;
  --marutai-paper:#f7f0df;
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 15% 8%, rgba(145,198,222,.12) 0 36px, transparent 37px),
    linear-gradient(180deg, #fffdf6 0%, var(--marutai-cream) 100%);
}
[data-testid="stHeader"], [data-testid="stToolbar"] { background: transparent; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display:none; }
.block-container { max-width:760px; padding-top:1.35rem; padding-bottom:7rem; }
h1,h2,h3,h4,p,div,button,input,label { font-family: "Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; }
h1,h2,h3,h4 { color:var(--marutai-navy); }
.stButton > button {
  min-height:54px; border-radius:17px; border:1px solid #eadfca;
  font-weight:800; font-size:1.05rem; color:var(--marutai-navy); background:#fffdfa;
  box-shadow:0 3px 10px rgba(79,55,22,.07);
}
.stButton > button[kind="primary"] {
  background:var(--marutai-red); color:#fff; border-color:var(--marutai-red);
}
.brand-fallback { display:flex; align-items:center; justify-content:center; gap:14px; margin:2px auto 15px; }
.brand-stamp {
  width:92px; height:92px; border:6px solid var(--marutai-red); border-radius:50%; color:var(--marutai-red);
  display:flex; align-items:center; justify-content:center; font-size:33px; font-weight:900; transform:rotate(-4deg);
  box-shadow:inset 0 0 0 3px #fff9ec;
}
.brand-title { color:var(--marutai-navy); font-weight:900; font-size:31px; line-height:1.0; letter-spacing:.02em; }
.brand-sub { color:var(--marutai-navy); font-weight:700; font-size:12px; margin-top:7px; }
.hero-question { color:var(--marutai-navy); text-align:center; font-size:1.25rem; font-weight:900; margin:.5rem 0 1rem; }
.count-card {
  margin-top:1.15rem; border:1px solid #eadfca; border-radius:20px; padding:18px 20px; text-align:center;
  background:linear-gradient(135deg,#fff,#f7fbff); box-shadow:0 3px 12px rgba(79,55,22,.07);
}
.count-card span { display:block; color:var(--marutai-navy); font-weight:800; }
.count-card strong { display:block; color:var(--marutai-red); font-size:3rem; line-height:1.05; margin-top:5px; }
[data-testid="stMetric"] { background:#fffdfa; border:1px solid #eadfca; border-radius:16px; padding:10px; }
[data-testid="stFileUploaderDropzone"], [data-testid="stCameraInput"] { border-radius:16px; }
hr { border-color:#e9dfcc; }
.nav-wrap { position:fixed; left:0; right:0; bottom:0; z-index:999; background:rgba(255,253,247,.96); border-top:1px solid #eadfca; padding:7px 10px 10px; backdrop-filter:blur(8px); }
.nav-inner { max-width:740px; margin:auto; display:grid; grid-template-columns:repeat(4,1fr); gap:6px; }
.nav-item { text-align:center; color:var(--marutai-navy); text-decoration:none; font-weight:800; font-size:.86rem; padding:6px 2px 4px; border-radius:12px; }
.nav-item.active { color:var(--marutai-red); background:#fff2ef; }
.nav-icon { display:block; font-size:1.45rem; line-height:1.05; margin-bottom:4px; }
@media (max-width: 640px) {
  .block-container { padding-left:.8rem; padding-right:.8rem; padding-top:.8rem; }
  .brand-title { font-size:27px; }
  .brand-stamp { width:80px; height:80px; font-size:29px; }
  h1 { font-size:2rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def go(page: str, **params: str) -> None:
    st.query_params.clear()
    st.query_params["page"] = page
    for key, value in params.items():
        if value not in (None, ""):
            st.query_params[key] = str(value)
    st.rerun()


def bottom_nav(active: str) -> None:
    items = [
        ("home", "⌂", "ホーム"),
        ("map", "🗺", "地図"),
        ("stampbook", "▣", "スタンプ帳"),
        ("facilities", "•••", "その他"),
    ]
    links = []
    for page, icon, label in items:
        cls = "nav-item active" if page == active else "nav-item"
        links.append(
            f'<a class="{cls}" href="?page={page}" target="_self"><span class="nav-icon">{icon}</span>{label}</a>'
        )
    st.markdown(f'<div class="nav-wrap"><div class="nav-inner">{"".join(links)}</div></div>', unsafe_allow_html=True)


page = st.query_params.get("page", "home")
routes = {
    "home": home.render,
    "map": map_page.render,
    "facilities": facilities.render,
    "visit": visit.render,
    "stampbook": stampbook.render,
}
routes.get(page, home.render)(go)
bottom_nav(page if page in routes else "home")
