# -*- coding: utf-8 -*-
"""
우리금융캐피탈 - 내 차에서 드림카까지 (체험형 데모)
"""
import base64
import json
import os
import smtplib
import urllib.request
from email.mime.text import MIMEText

import streamlit as st

import data

st.set_page_config(page_title="나에게 맞는 차량 찾기 | 우리금융캐피탈", page_icon="🚙", layout="wide")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "cars")
IMAGE_EXTS = ("jpg", "jpeg", "png", "webp", "avif")

# ---------------------------------------------------------------------------
# 스타일 (AI LAB 메인 + STOCK:ON 페이지의 다크 글래스 스타일)
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
:root{--bg:#071226;--surface:rgba(255,255,255,.04);--surface-2:rgba(255,255,255,.07);--border:rgba(255,255,255,.10);
--text:#e8eef8;--text-muted:#a3b3cf;--text-subtle:#7486a8;--accent:#60a5fa;--accent-strong:#3b82f6;
--violet:rgba(168,85,247,.7);--violet-glow:rgba(168,85,247,.18);}
.stApp :is(p,span,div,label,button,h1,h2,h3,h4,h5,li,input,textarea,a,td,th):not([data-testid="stIconMaterial"]){
  font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif;
  word-break:keep-all;}
.stApp{background:radial-gradient(900px 420px at 50% -8%,rgba(59,130,246,.22),transparent 70%),
  radial-gradient(600px 360px at 100% 30%,rgba(168,85,247,.10),transparent 70%),var(--bg);color:var(--text);}
header[data-testid="stHeader"],#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
.block-container{max-width:900px;padding:1.2rem 1rem 4rem;}
@keyframes dcUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.dc-hero,.dc-dark,.dc-card,.dc-top3,.dc-how>div,.dc-fleet>div,.dc-tblwrap{animation:dcUp .45s ease both;}

/* 상단 바 / 히어로 / STEP 탭 */
.dc-top{display:flex;align-items:center;justify-content:space-between;margin:4px 2px 18px;}
.dc-logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:15px;color:#fff;}
.dc-logo i{width:32px;height:32px;border-radius:10px;background:var(--surface-2);border:1px solid var(--border);color:#bae6fd;
  display:inline-flex;align-items:center;justify-content:center;font-style:normal;font-size:15px;}
.dc-brand{font-weight:700;color:var(--text-muted);font-size:14.5px;}
.dc-proto{display:inline-block;border:1px solid rgba(250,204,21,.55);color:#fde68a;background:rgba(250,204,21,.10);
  padding:2px 10px;border-radius:999px;font-size:.7rem;font-weight:800;letter-spacing:.12em;margin-left:8px;vertical-align:middle;}
.dc-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#102a43 0%,#0d3a6b 55%,#0067c8 125%);border-radius:28px;padding:44px 38px 30px;
  color:#fff;margin-bottom:16px;border:1px solid rgba(255,255,255,.10);box-shadow:0 20px 50px rgba(0,0,0,.35);}
.dc-hero:after{content:"";position:absolute;right:-90px;top:-90px;width:320px;height:320px;border-radius:50%;
  background:radial-gradient(circle,rgba(125,211,252,.35),transparent 65%);pointer-events:none;}
.dc-kick{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.08);
  border-radius:999px;padding:7px 14px;font-size:12.5px;letter-spacing:.14em;font-weight:800;color:#e0f2fe;}
.dc-kick:before{content:"";width:7px;height:7px;border-radius:50%;background:#7dd3fc;display:inline-block;}
.dc-hero h1.t{color:#fff;font-size:2.4rem;line-height:1.25;font-weight:800;margin:18px 0 14px;padding:0;position:relative;z-index:1;}
.dc-hero h1.t em{font-style:normal;color:#bae6fd;}
.dc-hero p{color:rgba(255,255,255,.84);font-size:1rem;line-height:1.7;margin:0;max-width:580px;position:relative;z-index:1;}
.dc-tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px;position:relative;z-index:1;}
.dc-tags span{border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.1);border-radius:999px;padding:7px 14px;font-size:.85rem;font-weight:700;color:#fff;}
.dc-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:26px;padding-top:22px;border-top:1px solid rgba(255,255,255,.14);position:relative;z-index:1;}
.dc-stats b{display:block;font-size:1.9rem;font-weight:800;color:#fff;line-height:1.1;}
.dc-stats span{display:block;font-size:.82rem;color:#bae6fd;margin-top:4px;font-weight:600;}
.dc-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(104px,1fr));gap:8px;margin-bottom:22px;
  background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:6px;}
.dc-chip{border-radius:13px;padding:10px 6px;text-align:center;background:rgba(96,165,250,.14);color:#bfdbfe;}
.dc-chip b{display:block;font-size:.82rem;font-weight:800;letter-spacing:.06em;}
.dc-chip span{display:block;font-size:.8rem;font-weight:600;margin-top:2px;}
.dc-chip.todo{background:transparent;color:var(--text-subtle);}
.dc-chip.now{background:rgba(255,255,255,.14);color:#fff;box-shadow:inset 0 0 0 1px rgba(255,255,255,.22);}

/* 카드 (유리 카드 + 보라 선택 글로우) */
.dc-card{background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:22px 24px;transition:all .15s ease;}
.dc-card.sel{border-color:var(--violet);box-shadow:0 0 24px var(--violet-glow);}
.dc-card .tt{font-size:1.12rem;font-weight:800;color:#fff;}
.dc-card .ds{font-size:.92rem;color:var(--text-muted);margin-top:6px;line-height:1.55;}
.dc-card .go{font-size:.85rem;font-weight:800;color:var(--accent);margin-top:12px;}
.dc-card.fork{min-height:200px;}
.dc-card .ic{font-size:1.9rem;margin-bottom:8px;}
.dc-card.fin{display:flex;gap:16px;align-items:flex-start;}
.dc-card.fin .ic{margin:0;width:52px;height:52px;border-radius:16px;background:var(--surface-2);border:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;font-size:1.6rem;flex:none;}
.dc-card.fin .sm{font-size:.88rem;font-weight:600;color:var(--text-muted);margin-left:8px;}
.dc-tagrow{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;}
.dc-tagrow span{background:rgba(96,165,250,.12);border:1px solid rgba(96,165,250,.25);color:#bfdbfe;border-radius:999px;padding:3px 10px;font-size:.76rem;font-weight:700;}
.dc-card.opt{display:flex;gap:14px;align-items:flex-start;min-height:104px;}
.dc-card.opt .lt{width:34px;height:34px;border-radius:11px;background:var(--surface-2);border:1px solid var(--border);color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-weight:800;flex:none;}
.dc-card.opt.sel .lt{background:rgba(168,85,247,.2);border-color:var(--violet);color:#e9d5ff;}
.dc-card.cmp{text-align:center;padding:18px 14px;}
.dc-card.cmp .nm{font-weight:800;font-size:.95rem;color:var(--text-muted);}
.dc-card.cmp .mo{font-size:1.9rem;font-weight:800;color:#fff;margin-top:6px;line-height:1.15;}
.dc-card.cmp .mo small{font-size:.95rem;font-weight:700;color:var(--text-muted);}
.dc-card.cmp .sb{font-size:.78rem;color:var(--text-subtle);margin-top:4px;}
[class*="st-key-card_"]{position:relative;margin-bottom:12px;}
[class*="st-key-card_"] [data-testid="stMarkdown"],[class*="st-key-card_"] [data-testid="stMarkdownContainer"]{margin-bottom:0!important;}
[class*="st-key-card_"] [data-testid="stElementContainer"]:has(button){position:absolute!important;inset:0!important;
  width:100%!important;height:100%!important;z-index:5;margin:0!important;}
[class*="st-key-card_"] [data-testid="stButton"]{width:100%!important;height:100%!important;}
[class*="st-key-card_"] [data-testid="stButton"] button{width:100%!important;height:100%!important;opacity:0;
  min-height:0!important;padding:0!important;cursor:pointer;}
[class*="st-key-card_"]:hover .dc-card,[class*="st-key-card_"]:hover .dc-top3{border-color:rgba(96,165,250,.65);transform:translateY(-2px);}
[class*="st-key-card_"]:hover .dc-card.sel,[class*="st-key-card_"]:hover .dc-top3.sel{border-color:var(--violet);}

/* 섹션 제목 / 진행 점 */
.dc-eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:var(--accent);text-transform:uppercase;}
.dc-ebrow{display:flex;justify-content:space-between;align-items:center;margin-top:6px;}
.dc-pill-s{background:rgba(96,165,250,.14);color:#bfdbfe;font-weight:800;font-size:.85rem;padding:5px 12px;border-radius:999px;border:1px solid rgba(96,165,250,.3);}
h2.dc-h2{font-size:1.45rem;font-weight:800;margin:6px 0 6px;padding:0;color:#fff;}
p.dc-sub{color:var(--text-muted);font-size:.95rem;margin:0 0 14px;line-height:1.6;}
p.dc-note{color:var(--text-subtle);font-size:.82rem;margin:4px 0 0;}
.dc-lbl{font-weight:800;font-size:.92rem;color:var(--text);margin:14px 0 6px;}
.dc-sec{margin:26px 0 4px;}
.dc-dots{display:flex;gap:6px;margin:4px 0 12px;}
.dc-dots i{height:6px;flex:1;border-radius:99px;background:rgba(255,255,255,.12);}
.dc-dots i.on{background:linear-gradient(90deg,#60a5fa,#a855f7);}
.dc-answers{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px;}
.dc-answers span{background:var(--surface-2);border:1px solid var(--border);border-radius:999px;padding:5px 12px;font-size:.8rem;font-weight:700;color:var(--text-muted);}

/* 시작 화면: 진행 안내 / 차량 미리보기 */
.dc-how{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:8px;}
.dc-how>div{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:16px;}
.dc-how em{font-style:normal;font-weight:800;color:var(--accent);font-size:.8rem;letter-spacing:.1em;}
.dc-how b{display:block;margin-top:6px;font-size:.98rem;color:#fff;}
.dc-how span{display:block;margin-top:4px;font-size:.82rem;color:var(--text-muted);line-height:1.5;}
.dc-fleet{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:8px;}
.dc-fleet>div{background:var(--surface);border:1px solid var(--border);border-radius:20px;overflow:hidden;}
.dc-fleet .im{background:#eef2f7;height:90px;display:flex;align-items:center;justify-content:center;}
.dc-fleet .im img{width:100%;height:100%;object-fit:contain;}
.dc-fleet .bd{padding:10px 12px 12px;}
.dc-fleet .bd b{display:block;font-size:.9rem;color:#fff;}
.dc-fleet .bd span{font-size:.78rem;color:var(--text-muted);}

/* 페르소나 / 견적 (메인 페이지 히어로 그라데이션) */
.dc-dark{background:linear-gradient(135deg,#102a43 0%,#0d3a6b 55%,#0067c8 125%);border-radius:28px;color:#fff;
  padding:26px 28px;border:1px solid rgba(255,255,255,.12);box-shadow:0 20px 50px rgba(0,0,0,.3);margin:6px 0 10px;}
.dc-persona{display:flex;gap:26px;align-items:center;}
.dc-persona .im{width:200px;height:170px;border-radius:20px;background:#e8edf5;flex:none;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.dc-persona .im img{width:100%;height:100%;object-fit:contain;}
.dc-persona .eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:#bae6fd;}
.dc-persona h3{color:#fff;font-size:1.9rem;font-weight:800;margin:6px 0 4px;padding:0;}
.dc-persona .sb{font-weight:800;font-size:1.02rem;margin-bottom:8px;color:#fff;}
.dc-persona .ds{color:rgba(255,255,255,.85);font-size:.95rem;line-height:1.6;}
.dc-persona .qt{color:#bae6fd;font-style:italic;margin-top:10px;font-size:.95rem;}

/* TOP3 카드 / 비교표 / 일치도 막대 */
.dc-top3{background:var(--surface);border:1px solid var(--border);border-radius:24px;overflow:hidden;transition:all .15s ease;}
.dc-top3.sel{border-color:var(--violet);box-shadow:0 0 24px var(--violet-glow);}
.dc-top3 .im{background:#eef2f7;height:138px;display:flex;align-items:center;justify-content:center;}
.dc-top3 .im img{width:100%;height:100%;object-fit:contain;}
.dc-top3 .bd{padding:14px 16px 16px;}
.dc-top3 .tg{font-size:.78rem;font-weight:800;color:var(--accent);letter-spacing:.06em;}
.dc-top3 .rw{display:flex;justify-content:space-between;align-items:baseline;gap:8px;}
.dc-top3 .nm{font-size:1.08rem;font-weight:800;margin-top:2px;color:#fff;}
.dc-top3 .mt{font-size:1.2rem;font-weight:800;color:var(--accent);}
.dc-top3 .ds{font-size:.82rem;color:var(--text-muted);margin:4px 0 8px;line-height:1.45;min-height:2.4em;}
.dc-top3 .pr{font-size:.85rem;color:var(--text-muted);font-weight:600;}
.dc-tblwrap{overflow-x:auto;background:var(--surface);border:1px solid var(--border);border-radius:20px;}
table.dc-tbl{width:100%;border-collapse:collapse;min-width:560px;}
table.dc-tbl th,table.dc-tbl td{padding:12px 14px;text-align:center;font-size:.9rem;border-bottom:1px solid var(--border);color:var(--text);}
table.dc-tbl th{font-weight:800;color:#fff;background:rgba(255,255,255,.04);}
table.dc-tbl td:first-child,table.dc-tbl th:first-child{text-align:left;color:var(--text-muted);font-weight:700;}
table.dc-tbl tr:last-child td{border-bottom:none;}
table.dc-tbl .hl{background:rgba(168,85,247,.10);}
.dc-bars{margin-top:12px;display:grid;gap:12px;}
.dc-bar .lb{display:flex;justify-content:space-between;font-size:.88rem;font-weight:700;color:var(--text-muted);margin-bottom:5px;}
.dc-bar .lb b{color:#fff;}
.dc-bar .tr{height:9px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden;}
.dc-bar .tr i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#60a5fa,#a855f7);}

/* 추천 설명 */
.dc-why{font-size:1rem;line-height:1.75;color:var(--text);}
.dc-ai{display:inline-block;background:rgba(168,85,247,.18);color:#d8b4fe;font-weight:800;font-size:.75rem;padding:3px 10px;border-radius:999px;margin-left:8px;border:1px solid rgba(168,85,247,.45);}

/* 견적 카드 */
.dc-quote .top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;}
.dc-quote .eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:#bae6fd;}
.dc-quote .sub{color:rgba(255,255,255,.88);margin-top:4px;font-size:.95rem;}
.dc-quote .big{font-size:2.7rem;font-weight:800;line-height:1.15;margin-top:2px;color:#fff;}
.dc-quote .big small{font-size:1.2rem;font-weight:700;}
.dc-chipw{background:rgba(255,255,255,.14);padding:8px 14px;border-radius:999px;font-weight:700;font-size:.88rem;border:1px solid rgba(255,255,255,.18);}
.dc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:18px;}
.dc-tile{background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:12px 14px;}
.dc-tile span{display:block;font-size:.8rem;color:#bae6fd;}
.dc-tile b{display:block;font-size:.98rem;margin-top:2px;color:#fff;}
.dc-quote .foot{font-size:.8rem;color:rgba(255,255,255,.7);margin-top:16px;}

/* 차량 상세 */
.dc-sumbar{display:flex;gap:8px;flex-wrap:wrap;margin:2px 0 14px;}
.dc-sumbar span{background:var(--surface-2);border:1px solid var(--border);border-radius:999px;padding:6px 13px;font-size:.82rem;font-weight:700;color:var(--text);}
.dc-sumbar span.hi{background:rgba(59,130,246,.2);border-color:rgba(96,165,250,.5);color:#dbeafe;}
.dc-imgbox{background:#eef2f7;border:1px solid var(--border);border-radius:24px;padding:10px;}
.dc-imgbox img{width:100%;display:block;border-radius:18px;}
.dc-swatch{display:inline-flex;align-items:center;margin-right:14px;font-size:.88rem;margin-bottom:6px;color:var(--text-muted);font-weight:600;}
.dc-swatch i{width:15px;height:15px;border-radius:50%;display:inline-block;margin-right:6px;border:1px solid rgba(255,255,255,.35);}

/* 세그먼트(pill 탭) */
div[data-testid="stRadio"] div[role="radiogroup"]{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:5px;gap:4px;flex-wrap:wrap;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"]{flex:1 1 auto;justify-content:center;padding:9px 14px;border-radius:12px;margin:0!important;cursor:pointer;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"]>div>div>div:first-child{display:none;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"] p{font-weight:700;color:var(--text-muted);font-size:.92rem;text-align:center;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"]{background:rgba(255,255,255,.14);box-shadow:inset 0 0 0 1px rgba(255,255,255,.18);}
div[data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"] p{color:#fff;font-weight:800;}

/* 버튼 */
div.stButton>button,div[data-testid="stFormSubmitButton"]>button{border-radius:14px;border:1px solid rgba(255,255,255,.14);
  background:rgba(255,255,255,.06);color:var(--text);font-weight:700;min-height:3.1rem;}
div.stButton>button:hover{border-color:rgba(96,165,250,.6);color:#fff;}
div.stButton>button[data-testid="stBaseButton-primary"],div[data-testid="stFormSubmitButton"]>button[data-testid="stBaseButton-primaryFormSubmit"]{
  background:linear-gradient(135deg,#3b82f6,#2563eb);border-color:#3b82f6;color:#fff;}
div[data-testid="stExpander"]{background:var(--surface);border:1px solid var(--border)!important;border-radius:18px;}
div[data-testid="stForm"]{background:var(--surface);border:1px solid var(--border);border-radius:20px;}
.dc-disclaimer{color:var(--text-subtle);font-size:.8rem;line-height:1.55;margin-top:22px;text-align:center;}

@media (max-width:640px){
  .dc-hero{padding:30px 22px 22px;} .dc-hero h1.t{font-size:1.7rem;}
  .dc-persona{flex-direction:column;align-items:stretch;} .dc-persona .im{width:100%;}
  .dc-grid{grid-template-columns:repeat(2,1fr);} .dc-quote .big{font-size:2.2rem;}
  .dc-dark{padding:22px 20px;} .dc-how{grid-template-columns:repeat(2,1fr);} .dc-fleet{grid-template-columns:repeat(2,1fr);}
  .dc-stats b{font-size:1.5rem;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 세션 상태
# ---------------------------------------------------------------------------
defaults = {
    "step": 0,
    "q_sub": 0,
    "has_car": None,
    "used_brand": None,
    "used_model": None,
    "used_year": None,
    "q1": None,
    "q2": None,
    "q3": None,
    "finance_id": None,
    "term_months": data.DEFAULT_TERM_MONTHS,
    "selected_car_id": None,
    "selected_color_idx": 0,
    "selected_trim_id": "standard",
    "selected_wheel_id": "18in",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def go(step, q_sub=0):
    st.session_state.step = step
    st.session_state.q_sub = q_sub
    st.rerun()


def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = v
    st.rerun()


def trade_in_price() -> int:
    """보유 차량이 있으면 중고차 시세(만원), 없으면 0."""
    if not st.session_state.has_car:
        return 0
    return data.get_used_price(st.session_state.used_brand, st.session_state.used_model,
                               st.session_state.used_year)


# ---------------------------------------------------------------------------
# 공통 UI 컴포넌트
# ---------------------------------------------------------------------------
def topbar():
    st.markdown(
        '<div class="dc-top"><div class="dc-logo"><i>✦</i>우리금융캐피탈</div>'
        '<div class="dc-brand">🚙 DREAM:CAR<span class="dc-proto">PROTOTYPE</span></div></div>',
        unsafe_allow_html=True,
    )


def step_chips(step_idx: int):
    """step_idx: 앱 단계(0=시작, 1=보유차량, 2=취향, 3=금융, 4=추천·견적, 5=만나보기)."""
    labels = ["내 차 가치 확인", "라이프스타일 분석", "금융조건 선택", "드림카 추천·견적", "차량 만나보기"]
    offset = 1
    if st.session_state.has_car is False:
        labels = labels[1:]
        offset = 2
    cur = -1 if step_idx <= 0 else step_idx - offset
    chips = []
    for i, label in enumerate(labels):
        cls = "dc-chip"
        if cur >= 0 and i > cur:
            cls += " todo"
        if i == cur:
            cls += " now"
        chips.append(f'<div class="{cls}"><b>STEP {i + 1:02d}</b><span>{label}</span></div>')
    st.markdown(f'<div class="dc-steps">{"".join(chips)}</div>', unsafe_allow_html=True)


def page_head(step_idx: int):
    topbar()
    step_chips(step_idx)


def section(eyebrow: str, title: str, sub: str = "", right: str = "", cls: str = ""):
    row = f'<div class="dc-ebrow"><span class="dc-eb">{eyebrow}</span>'
    if right:
        row += f'<span class="dc-pill-s">{right}</span>'
    row += "</div>"
    html = f'<div class="{cls}">' + row + f'<h2 class="dc-h2">{title}</h2>'
    if sub:
        html += f'<p class="dc-sub">{sub}</p>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def card_button(key: str, card_html: str) -> bool:
    """카드 전체가 클릭 영역인 버튼. 카드 HTML 위에 투명 버튼을 겹쳐 둔다."""
    with st.container(key=f"card_{key}"):
        st.markdown(card_html, unsafe_allow_html=True)
        return st.button("선택", key=f"btn_{key}")


def seg(options, state_key: str, widget_key: str, fmt=str, label="선택"):
    """세그먼트 컨트롤(라디오). 세션 값이 항상 기준이 되도록 위젯 값을 매번 동기화한다."""
    cur = st.session_state[state_key]
    if cur not in options:
        cur = options[0]
        st.session_state[state_key] = cur
    st.session_state[widget_key] = cur
    val = st.radio(label, options, format_func=fmt, horizontal=True, key=widget_key,
                   label_visibility="collapsed")
    if val != cur:
        st.session_state[state_key] = val
        st.rerun()
    return val


def disclaimer():
    st.markdown(
        '<div class="dc-disclaimer">※ 본 서비스는 전시·체험용 데모이며, 표시되는 차량 가격·중고차 시세·금리·월 납부금은 '
        '임의로 산정된 예시 값입니다.<br>실제 시세 및 금융조건은 우리금융캐피탈 상담을 통해 정확히 확인하시기 바랍니다.</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# 차량 이미지
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _image_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "jpeg" if ext == "jpg" else ext
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/{mime};base64,{b64}"


def _find_image(car_id: str, name: str):
    for ext in IMAGE_EXTS:
        path = os.path.join(ASSETS_DIR, car_id, f"{name}.{ext}")
        if os.path.exists(path):
            return path
    return None


def car_rep_uri(car: dict):
    """카드/페르소나에 쓸 대표 이미지: 첫 번째로 파일이 있는 색상 이미지."""
    for c in car["colors"]:
        p = _find_image(car["id"], c["id"])
        if p:
            return _image_data_uri(p)
    p = _find_image(car["id"], "photo")
    return _image_data_uri(p) if p else None


def car_placeholder_svg(hex_color: str) -> str:
    parts = [
        '<svg width="100%" viewBox="0 0 400 200" xmlns="http://www.w3.org/2000/svg">',
        '<ellipse cx="200" cy="176" rx="165" ry="9" fill="#00000018"/>',
        '<path d="M40,140 C40,120 55,110 80,108 L110,80 C120,68 140,60 165,60 L235,60 '
        'C258,60 278,68 288,80 L318,108 C345,110 360,120 360,140 L360,150 '
        'C360,158 353,164 345,164 L55,164 C47,164 40,158 40,150 Z" '
        f'fill="{hex_color}" stroke="#00000030" stroke-width="2"/>',
        '<path d="M120,108 L145,82 C152,74 162,70 172,70 L228,70 C238,70 248,74 255,82 L280,108 Z" '
        'fill="#dfeefc" fill-opacity="0.55"/>',
        '<line x1="200" y1="70" x2="200" y2="108" stroke="#00000030" stroke-width="2"/>',
        '<circle cx="118" cy="164" r="26" fill="#1c1c1c"/><circle cx="118" cy="164" r="11" fill="#9aa0a6"/>',
        '<circle cx="288" cy="164" r="26" fill="#1c1c1c"/><circle cx="288" cy="164" r="11" fill="#9aa0a6"/>',
        "</svg>",
    ]
    return "".join(parts)


def render_car_image(car: dict, color: dict):
    """색상별 사진 → 대표 사진+색상 합성 → 일러스트 순으로 보여준다."""
    path = _find_image(car["id"], color["id"])
    if path:
        st.markdown(f'<div class="dc-imgbox"><img src="{_image_data_uri(path)}"></div>', unsafe_allow_html=True)
        return
    path = _find_image(car["id"], "photo")
    if path:
        html = (
            '<div class="dc-imgbox"><div style="position:relative;border-radius:18px;overflow:hidden;">'
            f'<img src="{_image_data_uri(path)}" style="width:100%;display:block;">'
            f'<div style="position:absolute;inset:0;background:{color["hex"]};opacity:0.4;mix-blend-mode:color;"></div>'
            "</div></div>"
        )
        st.markdown(html, unsafe_allow_html=True)
        st.markdown('<p class="dc-note">※ 예시 사진에 선택한 색상을 합성한 이미지이며 실제와 다를 수 있어요.</p>',
                    unsafe_allow_html=True)
        return
    st.markdown(f'<div class="dc-imgbox" style="background:#f5f7fa;padding:18px;">{car_placeholder_svg(color["hex"])}</div>',
                unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 견적
# ---------------------------------------------------------------------------
def build_quote(total_price: int, finance_id=None) -> dict:
    used = trade_in_price()
    principal = max(total_price - used, 0)
    term = st.session_state.term_months
    fid = finance_id or st.session_state.finance_id
    monthly = data.calc_monthly_payment(fid, principal, total_price, term)
    return {"total": total_price, "used": used, "principal": principal, "term": term,
            "monthly": monthly, "total_pay": monthly * term}


def finance_name(fid=None) -> str:
    fid = fid or st.session_state.finance_id
    return next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == fid)


def quote_card(q: dict, extra_tiles=None):
    has_car = bool(st.session_state.has_car)
    car_txt = (f"{st.session_state.used_brand} {st.session_state.used_model} {st.session_state.used_year}년"
               if has_car else "보유차량 없음")
    title = "보상판매 반영 예상 월 납부금" if has_car else "예상 월 납부금"
    tiles = [
        ("신차가격", data.fmt_10k(q["total"])),
        ("내 차 시세", data.fmt_10k(q["used"])),
        ("원금" + (" (차량가−시세)" if has_car else " (차량가 전액)"), data.fmt_10k(q["principal"])),
        ("약정기간", f"{q['term']}개월"),
        ("현재 차량", car_txt),
        ("금융조건", finance_name()),
    ]
    tiles += extra_tiles or []
    tiles.append(("예상 총 납부액", data.fmt_10k(q["total_pay"])))
    grid = "".join(f'<div class="dc-tile"><span>{a}</span><b>{b}</b></div>' for a, b in tiles)
    monthly_txt = f'월 {q["monthly"]:,.1f}<small>만원</small>'
    html = (
        '<div class="dc-dark dc-quote"><div class="top"><div>'
        f'<div class="eb">DREAM CAR CHANGE QUOTE</div><div class="sub">{title}</div>'
        f'<div class="big">{monthly_txt}</div></div>'
        f'<div class="dc-chipw">{q["term"]}개월 · {finance_name()}</div></div>'
        f'<div class="dc-grid">{grid}</div>'
        '<div class="foot">※ 프로토타입 기준 · 실제 시세·금리·수수료·신용도·옵션에 따라 달라질 수 있습니다.</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 추천 설명 (OpenAI API, 키가 없으면 규칙 기반 문구)
# ---------------------------------------------------------------------------
def _openai_key():
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None


@st.cache_data(show_spinner=False, ttl=3600)
def _openai_explain(car_id: str, q1: int, q2: int, q3: int, has_car: bool, finance_id: str) -> str:
    car = data.get_car_by_id(car_id)
    fin = next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == finance_id)
    try:
        model = st.secrets["OPENAI_MODEL"]
    except Exception:
        model = "gpt-4o-mini"
    answers = [data.QUESTIONS[0]["options"][q1], data.QUESTIONS[1]["options"][q2],
               data.QUESTIONS[2]["options"][q3]]
    user = (
        f"추천 차량: {car['brand']} {car['model']} ({car['segment']})\n"
        f"차량 특징: {car['tagline']} / {car['desc']}\n"
        f"고객 취향 답변: 1) {answers[0]} 2) {answers[1]} 3) {answers[2]}\n"
        f"보유 차량 여부: {'있음(교체 고객)' if has_car else '없음(신규 고객)'}\n"
        f"선택한 금융조건: {fin}"
    )
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "당신은 우리금융캐피탈 체험존의 자동차 추천 도우미입니다. 고객의 취향 답변을 근거로 이 차량이 왜 어울리는지 "
                "한국어로 3~4문장, 친근하고 간결하게 설명하세요. 가격·금리·승인 가능 여부를 단정하거나 약속하지 말고, "
                "투자·금융 조언은 하지 마세요. 마크다운 없이 일반 문장으로만 쓰세요.")},
            {"role": "user", "content": user},
        ],
        "max_completion_tokens": 400,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {_openai_key()}"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        out = json.load(resp)
    return out["choices"][0]["message"]["content"].strip()


def recommendation_text(car: dict):
    q1, q2, q3 = st.session_state.q1, st.session_state.q2, st.session_state.q3
    has_car = bool(st.session_state.has_car)
    if _openai_key():
        try:
            return _openai_explain(car["id"], q1, q2, q3, has_car, st.session_state.finance_id), True
        except Exception:
            pass
    return data.explain_rule_based(car, q1, q2, q3, has_car), False


# ---------------------------------------------------------------------------
# 상담 신청 이메일
# ---------------------------------------------------------------------------
def send_consultation_email(payload: dict):
    try:
        gmail_user = st.secrets["GMAIL_USER"]
        gmail_pass = st.secrets["GMAIL_APP_PASSWORD"]
        recipient = st.secrets.get("RECIPIENT_EMAIL", gmail_user)
    except Exception:
        return False, "이메일 발송 기능이 아직 설정되지 않았습니다. (관리자: Streamlit Secrets에 GMAIL_USER / GMAIL_APP_PASSWORD 설정 필요)"

    lines = [
        f"신청자: {payload['name']} ({payload['phone']})",
        "",
        f"관심 차량: {payload['car_brand']} {payload['car_model']} - {payload['color_name']}",
        f"트림: {payload['trim_name']} / 휠: {payload['wheel_name']}",
        f"금융조건: {payload['finance_name']} · {payload['term']}개월",
        f"총 차량 가격: {payload['total_price']}",
    ]
    if payload["has_car"]:
        lines += [
            f"보유 차량: {payload['used_brand']} {payload['used_model']} ({payload['used_year']}년)",
            f"예상 중고차 판매가: {payload['used_price']}",
        ]
    else:
        lines.append("보유 차량: 없음")
    lines += [f"원금: {payload['principal']}", f"예상 월 납부금: {payload['monthly']}"]
    msg = MIMEText("\n".join(lines))
    msg["Subject"] = f"[차량매칭 체험존] 상담신청 - {payload['car_brand']} {payload['car_model']}"
    msg["From"] = gmail_user
    msg["To"] = recipient
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, [recipient], msg.as_string())
        return True, "상담 신청이 접수되어 담당자에게 이메일로 전달되었습니다."
    except Exception as e:
        return False, f"이메일 발송 중 오류가 발생했습니다: {e}"


# ---------------------------------------------------------------------------
# STEP 0: 시작 (소개 + 차량 보유 여부 분기)
# ---------------------------------------------------------------------------
def render_intro():
    topbar()
    n_cars = len(data.NEW_CAR_RECS)
    n_colors = sum(len(c["colors"]) for c in data.NEW_CAR_RECS)
    st.markdown(
        '<div class="dc-hero"><div class="dc-kick">MY CAR CHANGE JOURNEY</div>'
        '<h1 class="t">지금 타는 차에서,<br><em>다음 드림카까지.</em></h1>'
        '<p>내 차의 가치를 확인하고, 라이프스타일로 새 차를 추천받은 뒤 시세를 반영한 원금과 월 납부금까지 '
        '한 번에 확인해 보세요. 타는 차가 없어도 괜찮아요.</p>'
        '<div class="dc-tags"><span>내 차 시세</span><span>취향 매칭</span><span>AI 추천 설명</span><span>월 납부금 견적</span></div>'
        f'<div class="dc-stats"><div><b>{n_cars}</b><span>추천 후보 차종</span></div>'
        f'<div><b>{n_colors}</b><span>선택 가능한 색상</span></div>'
        '<div><b>3</b><span>할부 · 리스 · 렌트 견적</span></div></div></div>',
        unsafe_allow_html=True,
    )
    section("MY CURRENT CAR", "지금 타고 계신 차가 있으신가요?",
            "차량이 있다면 내 차 시세를 확인해 원금에 반영하고, 없다면 바로 드림카 찾기로 넘어갑니다.")
    c1, c2 = st.columns(2)
    with c1:
        if card_button("fork_has", '<div class="dc-card fork"><div class="ic">🚘</div><div class="tt">내 차가 있어요</div>'
                                   '<div class="ds">브랜드·차종·연식으로 예상 중고차 시세를 확인하고, 그만큼 원금에서 빼서 견적을 받아요</div>'
                                   '<div class="go">내 차 시세 확인하기 →</div></div>'):
            st.session_state.has_car = True
            go(1)
    with c2:
        if card_button("fork_none", '<div class="dc-card fork"><div class="ic">✨</div><div class="tt">차량이 없어요</div>'
                                    '<div class="ds">바로 취향을 알려주고 새 차를 추천받아요. 원금은 차량가 전액으로 계산돼요</div>'
                                    '<div class="go">드림카 바로 찾기 →</div></div>'):
            st.session_state.has_car = False
            st.session_state.used_brand = None
            st.session_state.used_model = None
            st.session_state.used_year = None
            go(2)

    section("HOW IT WORKS", "이렇게 진행돼요", "질문 3개와 금융조건 선택만으로 끝나요. 평균 1분이면 충분해요.", cls="dc-sec")
    steps = [("STEP 01", "내 차 시세 확인", "타는 차가 있다면 예상 판매가를 먼저 계산해요"),
             ("STEP 02", "라이프스타일 분석", "3가지 질문으로 나에게 맞는 차를 찾아요"),
             ("STEP 03", "금융조건 선택", "할부·리스·렌트 중 나에게 맞는 방식을 골라요"),
             ("STEP 04", "추천 · 견적", "추천 이유와 원금, 월 납부금을 한눈에 확인해요")]
    st.markdown('<div class="dc-how">' + "".join(
        f'<div><em>{a}</em><b>{b}</b><span>{c}</span></div>' for a, b, c in steps) + "</div>",
        unsafe_allow_html=True)

    section("DREAM CAR LINE-UP", "추천 후보 차량 미리보기", "취향에 따라 이런 차량들이 추천돼요.", cls="dc-sec")
    fleet = []
    for cid in ("ioniq5", "gv70", "bmw3", "santafe"):
        car = data.get_car_by_id(cid)
        uri = car_rep_uri(car)
        im = f'<div class="im"><img src="{uri}"></div>' if uri else '<div class="im">🚙</div>'
        fleet.append(f'<div>{im}<div class="bd"><b>{car["model"]}</b><span>{car["segment"]} · {data.fmt_10k(car["price"])}</span></div></div>')
    st.markdown('<div class="dc-fleet">' + "".join(fleet) + "</div>", unsafe_allow_html=True)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 1: 내 차 가치 확인
# ---------------------------------------------------------------------------
def render_used_car():
    page_head(1)
    section("STEP 01 · MY CAR VALUE", "지금 타시는 차를 알려주세요",
            "브랜드 · 차종 · 연식을 기준으로 예상 중고차 판매가를 확인해 드려요.")

    brands = list(data.USED_CAR_DB.keys())
    c1, c2, c3 = st.columns(3)
    brand = c1.selectbox("브랜드", brands, index=brands.index(st.session_state.used_brand)
                         if st.session_state.used_brand in brands else 0, key="sb_brand")
    models = list(data.USED_CAR_DB[brand].keys())
    if st.session_state.used_model not in models:
        st.session_state.used_model = models[0]
    model = c2.selectbox("차종", models, index=models.index(st.session_state.used_model), key="sb_model")
    years = list(data.USED_CAR_DB[brand][model]["years"])
    if st.session_state.used_year not in years:
        st.session_state.used_year = years[-1]
    year = c3.selectbox("연식", years, index=years.index(st.session_state.used_year), key="sb_year",
                        format_func=lambda y: f"{y}년")
    st.session_state.used_brand, st.session_state.used_model, st.session_state.used_year = brand, model, year

    info = data.USED_CAR_DB[brand][model]
    used_price = data.get_used_price(brand, model, year)
    age = max(data.CURRENT_YEAR - year, 0)
    retain = round(100 * used_price / info["new_price"])
    lo, hi = round(used_price * 0.95), round(used_price * 1.05)
    st.markdown(
        '<div class="dc-dark" style="margin-top:14px;"><div class="dc-eb" style="color:#bae6fd;">MY CAR VALUE</div>'
        f'<div style="font-size:.98rem;margin-top:4px;color:rgba(255,255,255,.88);">{brand} {model} · {year}년식 · {info["segment"]}</div>'
        f'<div style="font-size:2.6rem;font-weight:800;margin-top:4px;line-height:1.15;">{used_price:,}<small style="font-size:1.1rem;"> 만원</small></div>'
        f'<div class="dc-grid" style="grid-template-columns:repeat(3,1fr);">'
        f'<div class="dc-tile"><span>예상 시세 범위</span><b>{lo:,}~{hi:,}만원</b></div>'
        f'<div class="dc-tile"><span>차령</span><b>{age}년차</b></div>'
        f'<div class="dc-tile"><span>신차가 대비 잔존가치</span><b>{retain}%</b></div></div>'
        '<div class="foot" style="font-size:.8rem;color:rgba(255,255,255,.7);margin-top:14px;">'
        '예상 중고차 판매가는 신차 견적에서 원금으로 차감돼요.</div></div>',
        unsafe_allow_html=True,
    )
    n1, n2 = st.columns([1, 2])
    if n1.button("← 처음으로", use_container_width=True):
        go(0)
    if n2.button("라이프스타일 분석 시작 →", type="primary", use_container_width=True):
        go(2)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 2: 취향 질문 (선택하면 바로 다음으로)
# ---------------------------------------------------------------------------
def render_taste():
    page_head(2)
    q_sub = st.session_state.q_sub
    q = data.QUESTIONS[q_sub]
    section(f"MY DREAM CAR SIGNAL {q_sub + 1}", q["title"],
            "가장 가까운 선택지를 눌러 주세요. 선택하면 바로 다음으로 넘어가요.", right=f"{q_sub + 1} / 3")
    st.markdown('<div class="dc-dots">' + "".join(
        f'<i class="{"on" if i <= q_sub else ""}"></i>' for i in range(3)) + "</div>", unsafe_allow_html=True)
    prev = [data.QUESTIONS[i]["options"][st.session_state[data.QUESTIONS[i]["key"]]]
            for i in range(q_sub) if st.session_state.get(data.QUESTIONS[i]["key"]) is not None]
    if prev:
        st.markdown('<div class="dc-answers">' + "".join(f"<span>✓ {a}</span>" for a in prev) + "</div>",
                    unsafe_allow_html=True)

    selected = st.session_state.get(q["key"])
    descs = data.QUESTION_DESCS[q_sub]
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        with cols[i % 2]:
            sel = " sel" if selected == i else ""
            html = (f'<div class="dc-card opt{sel}"><div class="lt">{"ABCD"[i]}</div><div>'
                    f'<div class="tt">{opt}</div><div class="ds">{descs[i]}</div></div></div>')
            if card_button(f"q{q_sub}_{i}", html):
                st.session_state[q["key"]] = i
                if q_sub < 2:
                    st.session_state.q_sub += 1
                    st.rerun()
                else:
                    go(3)

    if st.button("← 이전", use_container_width=True):
        if q_sub == 0:
            go(1 if st.session_state.has_car else 0)
        else:
            st.session_state.q_sub -= 1
            st.rerun()
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 3: 금융조건 선택
# ---------------------------------------------------------------------------
def render_finance():
    page_head(3)
    section("STEP 03 · FINANCE", "원하시는 금융조건을 선택해 주세요",
            "카드를 누르면 바로 추천 결과로 넘어가요. 결과 화면에서 세 가지를 한눈에 비교할 수 있어요.")
    for opt in data.FINANCE_OPTIONS:
        sel = " sel" if st.session_state.finance_id == opt["id"] else ""
        tags = "".join(f"<span>{t}</span>" for t in opt["tags"])
        html = (f'<div class="dc-card fin{sel}"><div class="ic">{opt["icon"]}</div><div>'
                f'<div class="tt">{opt["name"]}<span class="sm">{opt["summary"]}</span></div>'
                f'<div class="ds">{opt["desc"]}</div><div class="dc-tagrow">{tags}</div></div></div>')
        if card_button(f"fin_{opt['id']}", html):
            st.session_state.finance_id = opt["id"]
            go(4)
    if st.button("← 이전", use_container_width=True):
        go(2, q_sub=2)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 4: 추천 결과 + 견적
# ---------------------------------------------------------------------------
def render_result():
    page_head(4)
    q1, q2, q3 = st.session_state.q1, st.session_state.q2, st.session_state.q3
    recs = data.recommend_cars(q1, q2, q3, top_n=3)
    if st.session_state.selected_car_id not in [c["id"] for c in recs]:
        st.session_state.selected_car_id = recs[0]["id"]
    car = data.get_car_by_id(st.session_state.selected_car_id)

    # 1) 페르소나
    persona = data.get_persona(q1)
    uri = car_rep_uri(car)
    img = f'<div class="im"><img src="{uri}"></div>' if uri else '<div class="im">🚙</div>'
    st.markdown(
        '<div class="dc-dark"><div class="dc-persona">' + img + '<div>'
        '<div class="eb">YOUR MOBILITY PERSONA</div>'
        f'<h3>{persona["name"]}</h3><div class="sb">{persona["title"]}</div>'
        f'<div class="ds">{persona["desc"]}</div><div class="qt">“{persona["quote"]}”</div></div></div></div>',
        unsafe_allow_html=True,
    )

    # 2) TOP 3
    section("DREAM CAR TOP 3", "당신에게 가장 잘 맞는 드림카 TOP 3",
            f"총 {len(data.NEW_CAR_RECS)}개 차종을 비교해 가장 적합한 3대만 추천했어요. 카드를 눌러 견적을 바꿔 보세요.",
            cls="dc-sec")
    cols = st.columns(3)
    for i, rc in enumerate(recs):
        sel = " sel" if rc["id"] == car["id"] else ""
        u = car_rep_uri(rc)
        im = f'<div class="im"><img src="{u}"></div>' if u else '<div class="im">🚙</div>'
        tag = f"TOP {i + 1}" + (" · 선택됨" if sel else "")
        html = (f'<div class="dc-top3{sel}">{im}<div class="bd"><div class="tg">{tag}</div>'
                f'<div class="rw"><div class="nm">{rc["model"]}</div>'
                f'<div class="mt">{data.match_percent(rc, q1, q2, q3)}%</div></div>'
                f'<div class="ds">{rc["tagline"]}</div><div class="pr">{data.fmt_10k(rc["price"])}</div></div></div>')
        with cols[i]:
            if card_button(f"top_{rc['id']}", html):
                st.session_state.selected_car_id = rc["id"]
                st.rerun()

    # 3) 추천 이유 (AI) + 취향 일치도
    with st.spinner("추천 이유를 정리하고 있어요…"):
        text, is_ai = recommendation_text(car)
    badge = '<span class="dc-ai">AI 추천 설명</span>' if is_ai else ""
    bars = "".join(
        f'<div class="dc-bar"><div class="lb"><span>{lab}</span><b>{pct}%</b></div>'
        f'<div class="tr"><i style="width:{max(pct, 6)}%"></i></div></div>'
        for lab, pct in data.match_breakdown(car, q1, q2, q3))
    st.markdown(
        f'<div class="dc-card" style="margin-top:6px;"><div class="dc-ebrow"><span class="dc-eb">WHY THIS CAR{badge}</span>'
        f'<span class="dc-pill-s">LIFESTYLE MATCH {data.match_percent(car, q1, q2, q3)}%</span></div>'
        f'<h2 class="dc-h2">{car["brand"]} {car["model"]}을(를) 추천드려요</h2><div class="dc-why">{text}</div>'
        + ('<p class="dc-note">※ AI가 작성한 설명이며 실제 상품 조건과 다를 수 있어요.</p>' if is_ai else "")
        + f'<div class="dc-bars">{bars}</div></div>',
        unsafe_allow_html=True,
    )

    # 4) TOP3 한눈에 비교표
    section("COMPARE", "TOP 3 한눈에 비교", f"선택한 금융조건({finance_name()} · {st.session_state.term_months}개월) 기준이에요.",
            cls="dc-sec")
    head = "".join(f'<th class="{"hl" if rc["id"] == car["id"] else ""}">{rc["model"]}</th>' for rc in recs)
    qs = [build_quote(rc["price"]) for rc in recs]

    def row(label, vals):
        cells = "".join(f'<td class="{"hl" if rc["id"] == car["id"] else ""}">{v}</td>' for rc, v in zip(recs, vals))
        return f"<tr><td>{label}</td>{cells}</tr>"

    table = (
        '<div class="dc-tblwrap"><table class="dc-tbl"><tr><th></th>' + head + "</tr>"
        + row("차급", [rc["segment"] for rc in recs])
        + row("차량가", [data.fmt_10k(rc["price"]) for rc in recs])
        + row("원금", [data.fmt_10k(x["principal"]) for x in qs])
        + row("월 납부금", [f'<b>{x["monthly"]:,.1f}만원</b>' for x in qs])
        + row("취향 매칭률", [f'{data.match_percent(rc, q1, q2, q3)}%' for rc in recs])
        + "</table></div>"
    )
    st.markdown(table, unsafe_allow_html=True)

    # 5) 금융 3종 비교 (카드 선택)
    section("FINANCE COMPARE", f"{car['model']} · 금융조건별 월 납부금", "카드를 누르면 아래 견적이 바뀌어요.", cls="dc-sec")
    fcols = st.columns(3)
    for i, fo in enumerate(data.FINANCE_OPTIONS):
        fq = build_quote(car["price"], fo["id"])
        sel = " sel" if st.session_state.finance_id == fo["id"] else ""
        html = (f'<div class="dc-card cmp{sel}"><div class="nm">{fo["icon"]} {fo["name"]}</div>'
                f'<div class="mo">{fq["monthly"]:,.1f}<small>만원/월</small></div>'
                f'<div class="sb">{st.session_state.term_months}개월 기준</div></div>')
        with fcols[i]:
            if card_button(f"cmp_{fo['id']}", html):
                st.session_state.finance_id = fo["id"]
                st.rerun()
    st.markdown('<div class="dc-lbl">약정기간</div>', unsafe_allow_html=True)
    seg([24, 36, 48, 60, 72], "term_months", "w_res_term", fmt=lambda m: f"{m}개월", label="약정기간")

    # 6) 견적
    quote_card(build_quote(car["price"]), extra_tiles=[("취향 매칭률", f"{data.match_percent(car, q1, q2, q3)}%")])

    if st.button("차량 만나보기 →", type="primary", use_container_width=True):
        go(5)
    c1, c2 = st.columns(2)
    if c1.button("추천 다시 받기", use_container_width=True):
        for k in ("q1", "q2", "q3", "selected_car_id"):
            st.session_state[k] = None
        go(2)
    if c2.button("처음부터", use_container_width=True):
        reset_all()
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 5: 차량 만나보기 (색상·트림·휠)
# ---------------------------------------------------------------------------
def render_detail():
    page_head(5)
    car = data.get_car_by_id(st.session_state.selected_car_id)
    if car is None:
        go(4)
        return
    q1, q2, q3 = st.session_state.q1, st.session_state.q2, st.session_state.q3
    if st.session_state.get("last_detail_car") != car["id"]:
        st.session_state.last_detail_car = car["id"]
        st.session_state.selected_color_idx = 0

    section("MEET YOUR DREAM CAR", f"{car['brand']} {car['model']}", car["desc"])

    with st.expander("추천 차량 · 금융조건 다시 선택하기"):
        recs = data.recommend_cars(q1, q2, q3, top_n=3)
        st.markdown('<div class="dc-lbl">추천 차량</div>', unsafe_allow_html=True)
        seg([r["id"] for r in recs], "selected_car_id", "w_det_car",
            fmt=lambda i: next(f'{r["brand"]} {r["model"]}' for r in recs if r["id"] == i), label="추천 차량")
        st.markdown('<div class="dc-lbl">금융조건</div>', unsafe_allow_html=True)
        seg([f["id"] for f in data.FINANCE_OPTIONS], "finance_id", "w_det_fin",
            fmt=lambda i: next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == i), label="금융조건")

    colors = car["colors"]
    st.markdown('<div class="dc-lbl">색상</div>', unsafe_allow_html=True)
    st.markdown("".join(f'<span class="dc-swatch"><i style="background:{c["hex"]}"></i>{c["name"]}</span>'
                        for c in colors), unsafe_allow_html=True)
    if st.session_state.selected_color_idx >= len(colors):
        st.session_state.selected_color_idx = 0
    cidx = seg(list(range(len(colors))), "selected_color_idx", f"w_color_{car['id']}",
               fmt=lambda i: colors[i]["name"], label="색상 선택")
    color = colors[cidx]
    render_car_image(car, color)
    st.markdown(f'<div style="text-align:center;margin:8px 0 4px;font-weight:800;">{color["name"]}</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="dc-lbl">트림</div>', unsafe_allow_html=True)
    tid = seg([t["id"] for t in data.TRIM_LEVELS], "selected_trim_id", f"w_trim_{car['id']}",
              fmt=lambda i: data.get_trim(i)["name"], label="트림")
    trim = data.get_trim(tid)
    st.markdown(f'<p class="dc-note">{trim["desc"]} ' + (f'(+{data.fmt_10k(trim["price_delta"])})'
                                                         if trim["price_delta"] else "(기본 포함)") + "</p>",
                unsafe_allow_html=True)
    st.markdown('<div class="dc-lbl">휠</div>', unsafe_allow_html=True)
    wid = seg([w["id"] for w in data.WHEEL_OPTIONS], "selected_wheel_id", f"w_wheel_{car['id']}",
              fmt=lambda i: data.get_wheel(i)["name"], label="휠")
    wheel = data.get_wheel(wid)

    st.markdown('<div class="dc-lbl">약정기간</div>', unsafe_allow_html=True)
    seg([24, 36, 48, 60, 72], "term_months", "w_det_term", fmt=lambda m: f"{m}개월", label="약정기간")

    total_price = car["price"] + trim["price_delta"] + wheel["price_delta"]
    q = build_quote(total_price)
    st.markdown(
        '<div class="dc-sec"><div class="dc-eb">MY SELECTION</div></div><div class="dc-sumbar">'
        f'<span>{car["brand"]} {car["model"]}</span><span>{color["name"]}</span><span>{trim["name"]}</span>'
        f'<span>{wheel["name"]}</span><span>{finance_name()} · {q["term"]}개월</span>'
        f'<span class="hi">월 {q["monthly"]:,.1f}만원</span></div>',
        unsafe_allow_html=True,
    )
    quote_card(q, extra_tiles=[("선택 색상", color["name"]), ("트림 · 휠", f'{trim["name"]} · {wheel["name"]}')])

    section("CONSULTING", "상담 신청하기", "이름과 연락처를 남기시면 담당자가 확인 후 연락드려요.", cls="dc-sec")
    with st.form("consult_form", clear_on_submit=True):
        name = st.text_input("이름")
        phone = st.text_input("연락처 (휴대폰 번호)", placeholder="010-0000-0000")
        submitted = st.form_submit_button("상담 신청하기", type="primary", use_container_width=True)
        if submitted:
            if not name.strip() or not phone.strip():
                st.warning("이름과 연락처를 입력해 주세요.")
            else:
                payload = {
                    "name": name.strip(), "phone": phone.strip(),
                    "car_brand": car["brand"], "car_model": car["model"], "color_name": color["name"],
                    "trim_name": trim["name"], "wheel_name": wheel["name"],
                    "finance_name": finance_name(), "term": q["term"],
                    "total_price": data.fmt_10k(total_price), "monthly": f"월 {data.fmt_10k(q['monthly'])}",
                    "has_car": bool(st.session_state.has_car),
                    "used_brand": st.session_state.used_brand, "used_model": st.session_state.used_model,
                    "used_year": st.session_state.used_year, "used_price": data.fmt_10k(q["used"]),
                    "principal": data.fmt_10k(q["principal"]),
                }
                ok, msg = send_consultation_email(payload)
                (st.success if ok else st.error)(msg)

    c1, c2 = st.columns(2)
    if c1.button("← 추천 결과로", use_container_width=True):
        go(4)
    if c2.button("처음부터", use_container_width=True):
        reset_all()
    disclaimer()


# ---------------------------------------------------------------------------
# 라우팅
# ---------------------------------------------------------------------------
ROUTES = {
    0: render_intro,
    1: render_used_car,
    2: render_taste,
    3: render_finance,
    4: render_result,
    5: render_detail,
}

ROUTES[st.session_state.step]()
