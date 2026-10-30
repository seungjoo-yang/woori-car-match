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
# 스타일 (부장님 드림카 페이지의 팔레트/카드 스타일 참고)
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
:root{--bg:#071226;--surface:rgba(255,255,255,.04);--surface-2:rgba(255,255,255,.07);--border:rgba(255,255,255,.10);
--text:#e8eef8;--text-muted:#a3b3cf;--text-subtle:#7486a8;--accent:#60a5fa;--accent-strong:#3b82f6;
--violet:rgba(168,85,247,.7);--violet-glow:rgba(168,85,247,.18);}
.stApp :is(p,span,div,label,button,h1,h2,h3,h4,h5,li,input,textarea,a):not([data-testid="stIconMaterial"]){
  font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif;
  word-break:keep-all;}
.stApp{background:radial-gradient(900px 420px at 50% -8%,rgba(59,130,246,.20),transparent 70%),var(--bg);color:var(--text);}
header[data-testid="stHeader"],#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
.block-container{max-width:880px;padding:1.2rem 1rem 4rem;}

/* 상단 바 / 히어로 / STEP 칩 */
.dc-top{display:flex;align-items:center;justify-content:space-between;margin:4px 2px 18px;}
.dc-logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:15px;color:#fff;}
.dc-logo i{width:32px;height:32px;border-radius:10px;background:var(--surface-2);border:1px solid var(--border);color:#bae6fd;
  display:inline-flex;align-items:center;justify-content:center;font-style:normal;font-size:15px;}
.dc-brand{font-weight:700;color:var(--text-muted);font-size:14.5px;}
.dc-proto{display:inline-block;border:1px solid rgba(250,204,21,.55);color:#fde68a;background:rgba(250,204,21,.10);
  padding:2px 10px;border-radius:999px;font-size:.7rem;font-weight:800;letter-spacing:.12em;margin-left:8px;vertical-align:middle;}
.dc-hero{background:linear-gradient(135deg,#102a43 0%,#0d3a6b 55%,#0067c8 125%);border-radius:28px;padding:42px 38px;
  color:#fff;margin-bottom:16px;border:1px solid rgba(255,255,255,.10);box-shadow:0 20px 50px rgba(0,0,0,.35);}
.dc-kick{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.08);
  border-radius:999px;padding:7px 14px;font-size:12.5px;letter-spacing:.14em;font-weight:800;color:#e0f2fe;}
.dc-kick:before{content:"";width:7px;height:7px;border-radius:50%;background:#7dd3fc;display:inline-block;}
.dc-hero h1.t{color:#fff;font-size:2.3rem;line-height:1.25;font-weight:800;margin:18px 0 14px;padding:0;}
.dc-hero h1.t em{font-style:normal;color:#bae6fd;}
.dc-hero p{color:rgba(255,255,255,.84);font-size:1rem;line-height:1.7;margin:0;max-width:580px;}
.dc-tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px;}
.dc-tags span{border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.1);border-radius:999px;padding:7px 14px;font-size:.85rem;font-weight:700;color:#fff;}
.dc-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(104px,1fr));gap:8px;margin-bottom:20px;
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
.dc-card.fork{min-height:168px;}
.dc-card .ic{font-size:1.9rem;margin-bottom:8px;}
.dc-card.fin{display:flex;gap:16px;align-items:flex-start;}
.dc-card.fin .ic{margin:0;width:52px;height:52px;border-radius:16px;background:var(--surface-2);border:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;font-size:1.6rem;flex:none;}
.dc-card.fin .sm{font-size:.88rem;font-weight:600;color:var(--text-muted);margin-left:8px;}
.dc-card.opt{min-height:96px;}
[class*="st-key-card_"]{position:relative;margin-bottom:12px;}
[class*="st-key-card_"] [data-testid="stElementContainer"]:has(button){position:absolute;inset:0;z-index:5;margin:0;}
[class*="st-key-card_"] [data-testid="stButton"],[class*="st-key-card_"] [data-testid="stButton"] button{
  width:100%;height:100%;opacity:0;min-height:0;cursor:pointer;}
[class*="st-key-card_"]:hover .dc-card,[class*="st-key-card_"]:hover .dc-top3{border-color:rgba(96,165,250,.65);transform:translateY(-2px);}
[class*="st-key-card_"]:hover .dc-card.sel,[class*="st-key-card_"]:hover .dc-top3.sel{border-color:var(--violet);}

/* 섹션 제목 */
.dc-eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:var(--accent);text-transform:uppercase;}
.dc-ebrow{display:flex;justify-content:space-between;align-items:center;margin-top:6px;}
.dc-pill-s{background:rgba(96,165,250,.14);color:#bfdbfe;font-weight:800;font-size:.85rem;padding:5px 12px;border-radius:999px;border:1px solid rgba(96,165,250,.3);}
h2.dc-h2{font-size:1.45rem;font-weight:800;margin:6px 0 6px;padding:0;color:#fff;}
p.dc-sub{color:var(--text-muted);font-size:.95rem;margin:0 0 14px;line-height:1.6;}
p.dc-note{color:var(--text-subtle);font-size:.82rem;margin:4px 0 0;}
.dc-lbl{font-weight:800;font-size:.92rem;color:var(--text);margin:14px 0 6px;}

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

/* TOP3 카드 */
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

/* 차량 이미지 박스 */
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
  .dc-hero{padding:30px 22px;} .dc-hero h1.t{font-size:1.7rem;}
  .dc-persona{flex-direction:column;align-items:stretch;} .dc-persona .im{width:100%;}
  .dc-grid{grid-template-columns:repeat(2,1fr);} .dc-quote .big{font-size:2.2rem;}
  .dc-dark{padding:22px 20px;}
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


def section(eyebrow: str, title: str, sub: str = "", right: str = ""):
    row = f'<div class="dc-ebrow"><span class="dc-eb">{eyebrow}</span>'
    if right:
        row += f'<span class="dc-pill-s">{right}</span>'
    row += "</div>"
    html = row + f'<h2 class="dc-h2">{title}</h2>'
    if sub:
        html += f'<p class="dc-sub">{sub}</p>'
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
def build_quote(total_price: int) -> dict:
    used = trade_in_price()
    principal = max(total_price - used, 0)
    term = st.session_state.term_months
    monthly = data.calc_monthly_payment(st.session_state.finance_id, principal, total_price, term)
    return {"total": total_price, "used": used, "principal": principal, "term": term,
            "monthly": monthly, "total_pay": monthly * term}


def finance_name() -> str:
    return next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == st.session_state.finance_id)


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
# STEP 0: 시작 (차량 보유 여부 분기)
# ---------------------------------------------------------------------------
def render_intro():
    topbar()
    st.markdown(
        '<div class="dc-hero"><div class="dc-kick">MY CAR CHANGE JOURNEY</div>'
        '<h1 class="t">지금 타는 차에서,<br><em>다음 드림카까지.</em></h1>'
        '<p>내 차의 가치를 확인하고, 라이프스타일로 새 차를 추천받은 뒤 시세를 반영한 원금과 월 납부금까지 '
        '한 번에 확인해 보세요. 타는 차가 없어도 괜찮아요.</p>'
        '<div class="dc-tags"><span>내 차 시세</span><span>취향 매칭</span><span>AI 추천 설명</span><span>월 납부금 견적</span></div></div>',
        unsafe_allow_html=True,
    )
    step_chips(0)
    section("MY CURRENT CAR", "지금 타고 계신 차가 있으신가요?",
            "차량이 있다면 내 차 시세를 확인해 원금에 반영하고, 없다면 바로 드림카 찾기로 넘어갑니다.")
    c1, c2 = st.columns(2)
    with c1:
        if card_button("fork_has", '<div class="dc-card fork"><div class="ic">🚘</div><div class="tt">내 차가 있어요</div>'
                                   '<div class="ds">브랜드·차종·연식으로 예상 중고차 시세를 확인해요</div>'
                                   '<div class="go">내 차 시세 확인하기 →</div></div>'):
            st.session_state.has_car = True
            go(1)
    with c2:
        if card_button("fork_none", '<div class="dc-card fork"><div class="ic">✨</div><div class="tt">차량이 없어요</div>'
                                    '<div class="ds">바로 취향을 알려주고 새 차를 추천받아요</div>'
                                    '<div class="go">드림카 바로 찾기 →</div></div>'):
            st.session_state.has_car = False
            st.session_state.used_brand = None
            st.session_state.used_model = None
            st.session_state.used_year = None
            go(2)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 1: 내 차 가치 확인
# ---------------------------------------------------------------------------
def render_used_car():
    page_head(1)
    section("STEP 01 · MY CAR VALUE", "지금 타시는 차를 알려주세요",
            "브랜드 · 차종 · 연식을 기준으로 예상 중고차 판매가를 확인해 드려요.")

    brands = list(data.USED_CAR_DB.keys())
    brand = st.selectbox("브랜드", brands, index=brands.index(st.session_state.used_brand)
                         if st.session_state.used_brand in brands else 0, key="sb_brand")
    models = list(data.USED_CAR_DB[brand].keys())
    if st.session_state.used_model not in models:
        st.session_state.used_model = models[0]
    model = st.selectbox("차종", models, index=models.index(st.session_state.used_model), key="sb_model")
    years = list(data.USED_CAR_DB[brand][model]["years"])
    if st.session_state.used_year not in years:
        st.session_state.used_year = years[-1]
    year = st.selectbox("연식", years, index=years.index(st.session_state.used_year), key="sb_year",
                        format_func=lambda y: f"{y}년")
    st.session_state.used_brand, st.session_state.used_model, st.session_state.used_year = brand, model, year

    used_price = data.get_used_price(brand, model, year)
    segment = data.USED_CAR_DB[brand][model]["segment"]
    st.markdown(
        '<div class="dc-dark" style="margin-top:14px;"><div class="dc-eb" style="color:#c7d2fe;">MY CAR VALUE</div>'
        f'<div style="font-size:.98rem;margin-top:4px;color:rgba(255,255,255,.85);">{brand} {model} · {year}년 · {segment}</div>'
        f'<div style="font-size:2.4rem;font-weight:800;margin-top:4px;">{used_price:,}<small style="font-size:1.1rem;"> 만원</small></div>'
        '<div style="font-size:.85rem;color:rgba(255,255,255,.7);margin-top:6px;">예상 중고차 판매가 · 신차 견적에서 원금으로 차감돼요</div></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([1, 2])
    if c1.button("← 처음으로", use_container_width=True):
        go(0)
    if c2.button("라이프스타일 분석 시작 →", type="primary", use_container_width=True):
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

    selected = st.session_state.get(q["key"])
    cols = st.columns(2)
    for i, opt in enumerate(q["options"]):
        with cols[i % 2]:
            sel = " sel" if selected == i else ""
            if card_button(f"q{q_sub}_{i}", f'<div class="dc-card opt{sel}"><div class="tt">{opt}</div>'
                                            '<div class="go">이 선택으로 진행 →</div></div>'):
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
            "카드를 누르면 바로 추천 결과로 넘어가요. 결과 화면에서 언제든 바꿀 수 있어요.")
    for opt in data.FINANCE_OPTIONS:
        sel = " sel" if st.session_state.finance_id == opt["id"] else ""
        html = (f'<div class="dc-card fin{sel}"><div class="ic">{opt["icon"]}</div><div>'
                f'<div class="tt">{opt["name"]}<span class="sm">{opt["summary"]}</span></div>'
                f'<div class="ds">{opt["desc"]}</div></div></div>')
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

    # 추천 이유
    with st.spinner("추천 이유를 정리하고 있어요…"):
        text, is_ai = recommendation_text(car)
    badge = '<span class="dc-ai">AI 추천 설명</span>' if is_ai else ""
    st.markdown(
        f'<div class="dc-card"><div class="dc-eb">WHY THIS CAR{badge}</div>'
        f'<h2 class="dc-h2">{car["brand"]} {car["model"]}을(를) 추천드려요</h2><div class="dc-why">{text}</div>'
        + ('<p class="dc-note">※ AI가 작성한 설명이며 실제 상품 조건과 다를 수 있어요.</p>' if is_ai else "")
        + "</div>",
        unsafe_allow_html=True,
    )

    # TOP 3
    section("DREAM CAR TOP 3", "당신에게 가장 잘 맞는 드림카 TOP 3",
            f"총 {len(data.NEW_CAR_RECS)}개 차종을 비교해 가장 적합한 3대만 추천했어요. 카드를 눌러 견적을 바꿔 보세요.")
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

    st.markdown(
        '<div class="dc-card" style="margin-top:6px;"><div class="dc-ebrow"><span class="dc-eb">YOUR DREAM CAR</span>'
        f'<span class="dc-pill-s">LIFESTYLE MATCH {data.match_percent(car, q1, q2, q3)}%</span></div>'
        f'<h2 class="dc-h2">{car["brand"]} {car["model"]}</h2>'
        f'<p class="dc-sub" style="margin:0;">{car["segment"]} · {car["tagline"]}</p></div>',
        unsafe_allow_html=True,
    )

    # 견적 조건
    st.markdown('<div class="dc-card" style="margin-top:10px;"><div class="dc-eb">MY QUOTE</div>'
                '<h2 class="dc-h2" style="font-size:1.2rem;">내 견적 조건</h2>'
                '<p class="dc-sub" style="margin:0;">금융조건과 약정기간을 고르면 월 납부금이 바로 다시 계산돼요.</p></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="dc-lbl">금융조건</div>', unsafe_allow_html=True)
    seg([f["id"] for f in data.FINANCE_OPTIONS], "finance_id", "w_res_fin",
        fmt=lambda i: next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == i), label="금융조건")
    st.markdown('<div class="dc-lbl">약정기간</div>', unsafe_allow_html=True)
    seg([24, 36, 48, 60, 72], "term_months", "w_res_term", fmt=lambda m: f"{m}개월", label="약정기간")

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
    quote_card(q, extra_tiles=[("선택 색상", color["name"]), ("트림 · 휠", f'{trim["name"]} · {wheel["name"]}')])

    section("CONSULTING", "상담 신청하기", "이름과 연락처를 남기시면 담당자가 확인 후 연락드려요.")
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
