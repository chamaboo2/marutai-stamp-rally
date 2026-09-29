from __future__ import annotations

import streamlit as st

from pages import facilities, home, map as map_page, stampbook, visit
from services.storage_service import init_storage

st.set_page_config(
    page_title="まるたいスタンプラリー",
    page_icon="♨️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CSS = r"""
<style>
:root {
  color-scheme: light !important;
  --marutai-red:#d9362b;
  --marutai-red-soft:#fff0ed;
  --marutai-navy:#173a5e;
  --marutai-navy-2:#244f78;
  --marutai-cream:#fffaf0;
  --marutai-paper:#f7f0df;
  --marutai-white:#ffffff;
  --marutai-border:#e7dcc7;
  --marutai-blue:#dceef5;
  --marutai-muted:#6b7785;
}
html, body, [data-testid="stAppViewContainer"], .stApp {
  color-scheme: light !important;
  background-color:var(--marutai-cream) !important;
  color:var(--marutai-navy) !important;
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 14% 7%, rgba(166,210,227,.14) 0 32px, transparent 33px),
    linear-gradient(180deg, #fffdf8 0%, var(--marutai-cream) 100%) !important;
}
[data-testid="stHeader"] { background:rgba(255,253,248,.96) !important; height:2.25rem; }
[data-testid="stToolbar"], [data-testid="stDecoration"] { background:transparent !important; }
[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display:none !important; }
.block-container {
  max-width:760px;
  padding-top:.35rem !important;
  padding-bottom:8.5rem !important;
}

/* Typography: never place white body text on cream */
.stApp, .stApp p, .stApp li, .stApp label,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"],
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
  color:var(--marutai-navy) !important;
}
h1,h2,h3,h4,h5,h6 {
  color:var(--marutai-navy) !important;
  letter-spacing:.01em;
}
h1 { margin-top:.15rem !important; margin-bottom:.55rem !important; }
h2,h3 { margin-top:.65rem !important; margin-bottom:.45rem !important; }
[data-testid="stCaptionContainer"] { color:#516982 !important; }
small { color:#516982 !important; }
hr { border-color:var(--marutai-border) !important; }

/* Buttons */
.stButton > button, .stLinkButton > a {
  min-height:48px;
  border-radius:15px !important;
  border:1px solid var(--marutai-border) !important;
  font-weight:800 !important;
  font-size:1rem !important;
  color:var(--marutai-navy) !important;
  background:var(--marutai-white) !important;
  box-shadow:0 2px 8px rgba(57,43,20,.05) !important;
}
.stButton > button:hover, .stLinkButton > a:hover {
  border-color:#d9a59f !important;
  background:#fff8f6 !important;
  color:var(--marutai-navy) !important;
}
.stButton > button[kind="primary"] {
  background:var(--marutai-red) !important;
  color:#fff !important;
  border-color:var(--marutai-red) !important;
}
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span { color:#fff !important; }

/* Streamlit form widgets: force light appearance even when device/browser is dark */
[data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="select"] > div, [data-baseweb="select"] input,
[data-testid="stDateInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="input"] {
  background:var(--marutai-white) !important;
  color:var(--marutai-navy) !important;
  border-color:var(--marutai-border) !important;
}
[data-baseweb="input"] input, [data-baseweb="base-input"] input,
[data-baseweb="select"] input, [data-testid="stTextInput"] input {
  color:var(--marutai-navy) !important;
  -webkit-text-fill-color:var(--marutai-navy) !important;
  background:transparent !important;
}
input::placeholder, textarea::placeholder {
  color:#8a929b !important;
  -webkit-text-fill-color:#8a929b !important;
  opacity:1 !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] div,
[data-testid="stSelectbox"] span, [data-testid="stMultiSelect"] span {
  color:var(--marutai-navy) !important;
}
[data-baseweb="tag"] {
  background:var(--marutai-red-soft) !important;
  color:var(--marutai-navy) !important;
  border:1px solid #efc3bd !important;
}
[data-baseweb="tag"] span { color:var(--marutai-navy) !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
  background:var(--marutai-white) !important;
  color:var(--marutai-navy) !important;
}
[role="option"] { background:var(--marutai-white) !important; color:var(--marutai-navy) !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] {
  background:var(--marutai-red-soft) !important;
  color:var(--marutai-navy) !important;
}

/* Expander */
[data-testid="stExpander"] {
  background:rgba(255,255,255,.88) !important;
  border:1px solid var(--marutai-border) !important;
  border-radius:16px !important;
  box-shadow:none !important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p,
[data-testid="stExpander"] svg { color:var(--marutai-navy) !important; fill:var(--marutai-navy) !important; }

/* Checkbox/radio */
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] p,
[data-testid="stRadio"] label, [data-testid="stRadio"] p {
  color:var(--marutai-navy) !important;
  opacity:1 !important;
}
[data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child,
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
  border-color:#8ea3b7 !important;
  background:#fff !important;
}
[data-testid="stCheckbox"] [aria-checked="true"] > div:first-child,
[data-testid="stRadio"] [aria-checked="true"] > div:first-child {
  background:var(--marutai-red) !important;
  border-color:var(--marutai-red) !important;
}

/* Segmented control */
[data-testid="stSegmentedControl"] { background:transparent !important; }
[data-testid="stSegmentedControl"] button {
  color:var(--marutai-navy) !important;
  background:#fff !important;
  border-color:var(--marutai-border) !important;
}
[data-testid="stSegmentedControl"] button[aria-pressed="true"] {
  background:var(--marutai-red-soft) !important;
  color:var(--marutai-red) !important;
  border-color:#e7aaa3 !important;
}

/* Uploader / camera */
[data-testid="stFileUploader"], [data-testid="stCameraInput"] { color:var(--marutai-navy) !important; }
[data-testid="stFileUploaderDropzone"] {
  background:#fff !important;
  border:1px dashed #c8bca8 !important;
  border-radius:16px !important;
}
[data-testid="stFileUploaderDropzone"] * { color:var(--marutai-navy) !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div { display:none !important; }
[data-testid="stFileUploaderDropzoneInstructions"]::before {
  content:"写真をここに追加";
  display:block;
  color:var(--marutai-navy);
  font-weight:800;
  margin-bottom:2px;
}
[data-testid="stFileUploaderDropzoneInstructions"]::after {
  content:"JPG・PNG・WEBP";
  display:block;
  color:var(--marutai-muted);
  font-size:.78rem;
}
[data-testid="stFileUploaderDropzone"] button { font-size:0 !important; }
[data-testid="stFileUploaderDropzone"] button::after {
  content:"写真を選ぶ";
  font-size:.9rem;
  color:var(--marutai-navy);
  font-weight:800;
}

/* Status boxes */
[data-testid="stAlert"] { border-radius:14px !important; }
[data-testid="stAlert"] p { color:var(--marutai-navy) !important; }

/* Brand */
.brand-fallback { display:flex; align-items:center; justify-content:center; gap:14px; margin:0 auto 10px; }
.brand-stamp {
  width:84px; height:84px; border:6px solid var(--marutai-red); border-radius:50%; color:var(--marutai-red);
  display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:900; transform:rotate(-4deg);
  box-shadow:inset 0 0 0 3px #fff9ec;
}
.brand-title { color:var(--marutai-navy); font-weight:900; font-size:29px; line-height:1.02; letter-spacing:.02em; }
.brand-sub { color:var(--marutai-navy); font-weight:700; font-size:12px; margin-top:6px; }
.hero-question { color:var(--marutai-navy); text-align:center; font-size:1.18rem; font-weight:900; margin:.25rem 0 .75rem; }
.count-card {
  margin-top:.9rem; border:1px solid var(--marutai-border); border-radius:18px; padding:15px 18px; text-align:center;
  background:linear-gradient(135deg,#fff,#f7fbff); box-shadow:0 2px 10px rgba(79,55,22,.05);
}
.count-card span { display:block; color:var(--marutai-navy); font-weight:800; }
.count-card strong { display:block; color:var(--marutai-red); font-size:2.7rem; line-height:1.05; margin-top:4px; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--marutai-border); border-radius:14px; padding:9px; }

/* Facility cards */
.facility-card {
  border:1px solid var(--marutai-border);
  border-radius:17px;
  padding:14px 15px 11px;
  margin:.4rem 0 .18rem;
  background:rgba(255,255,255,.94);
  box-shadow:0 2px 9px rgba(55,40,18,.045);
}
.facility-card-title { color:var(--marutai-navy); font-weight:900; font-size:1.2rem; line-height:1.25; margin-bottom:7px; }
.facility-card-meta { color:#385672; font-size:.9rem; font-weight:700; margin-bottom:7px; }
.facility-tags { display:flex; flex-wrap:wrap; gap:6px; margin:5px 0 4px; }
.facility-tag {
  display:inline-flex; align-items:center; min-height:28px; padding:3px 9px; border-radius:999px;
  border:1px solid #d6e0e8; background:#f7fbfd; color:var(--marutai-navy); font-size:.82rem; font-weight:700;
}
.facility-tag.yes { border-color:#b8d9e5; background:#eff9fc; }
.facility-tag.no { border-color:#e2ddd4; background:#fbfaf7; color:#687889; }
.facility-status { margin-top:7px; color:var(--marutai-navy); font-weight:900; font-size:.9rem; }
.facility-status.visited { color:var(--marutai-red); }
.facility-card + div[data-testid="stButton"] button { min-height:42px !important; }

/* Detail */
.detail-summary {
  background:#fff; border:1px solid var(--marutai-border); border-radius:16px; padding:12px 14px; margin:.2rem 0 .6rem;
  color:var(--marutai-navy);
}
.detail-summary strong { color:var(--marutai-navy); }

/* Bottom navigation */
.nav-wrap {
  position:fixed; left:0; right:0; bottom:0; z-index:9999;
  background:rgba(255,253,248,.98); border-top:1px solid var(--marutai-border);
  padding:6px max(10px, env(safe-area-inset-right)) calc(8px + env(safe-area-inset-bottom)) max(10px, env(safe-area-inset-left));
  backdrop-filter:blur(9px);
}
.nav-inner { max-width:740px; margin:auto; display:grid; grid-template-columns:repeat(4,1fr); gap:5px; }
.nav-item {
  position:relative; text-align:center; color:var(--marutai-navy) !important; text-decoration:none !important;
  font-weight:800; font-size:.79rem; padding:6px 2px 7px; border-radius:11px;
}
.nav-item.active { color:var(--marutai-red) !important; background:var(--marutai-red-soft); }
.nav-item.active::after {
  content:""; position:absolute; left:24%; right:24%; bottom:2px; height:3px; border-radius:3px; background:var(--marutai-red);
}
.nav-icon { display:block; font-size:1.35rem; line-height:1.05; margin-bottom:3px; }

/* Map iframe */
[data-testid="stIFrame"] { border-radius:16px; overflow:hidden; }

@media (max-width: 640px) {
  [data-testid="stHeader"] { height:1.75rem; }
  .block-container {
    padding-left:.72rem !important;
    padding-right:.72rem !important;
    padding-top:.1rem !important;
    padding-bottom:9.2rem !important;
  }
  h1 { font-size:1.72rem !important; line-height:1.16 !important; margin:.1rem 0 .45rem !important; }
  h2 { font-size:1.4rem !important; }
  h3 { font-size:1.12rem !important; }
  .brand-title { font-size:25px; }
  .brand-stamp { width:72px; height:72px; font-size:26px; }
  .hero-question { font-size:1.08rem; margin:.15rem 0 .6rem; }
  .stButton > button, .stLinkButton > a { min-height:46px; font-size:.95rem !important; }
  .facility-card { padding:12px 12px 10px; border-radius:15px; }
  .facility-card-title { font-size:1.1rem; }
  .facility-card-meta, .facility-status { font-size:.86rem; }
  .facility-tag { font-size:.78rem; padding:2px 8px; }
  [data-testid="stExpander"] details > div { padding-left:.6rem !important; padding-right:.6rem !important; }
  [data-testid="stVerticalBlock"] { gap:.55rem !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
init_storage()


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
