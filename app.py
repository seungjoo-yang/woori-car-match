# -*- coding: utf-8 -*-
"""
우리금융캐피탈 - 나에게 맞는 차량 찾기 (체험형 데모)
"""
import base64
import os
import smtplib
from email.mime.text import MIMEText

import streamlit as st

import data

st.set_page_config(page_title="나에게 맞는 차량 찾기 | 우리금융캐피탈", page_icon="🚗", layout="wide")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "cars")

STEP_LABELS = ["보유 차량", "취향 분석", "금융조건", "추천 결과", "차량 만나보기"]

# ---------------------------------------------------------------------------
# 스타일
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"]  { font-size: 17px; }
    .block-container { max-width: 900px; padding-top: 1.6rem; padding-bottom: 4rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    div.stButton > button {
        min-height: 3.4rem;
        font-size: 1.05rem;
        border-radius: 14px;
        white-space: normal;
        line-height: 1.3rem;
    }
    div.stButton > button[kind="primary"] {
        border: 2px solid #003876;
        box-shadow: 0 2px 10px rgba(0,56,118,0.18);
    }
    .brand-banner {
        background: linear-gradient(135deg, #003876 0%, #0a5ea8 100%);
        color: white;
        padding: 1.1rem 1.4rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
    }
    .brand-banner h1 { font-size: 1.3rem; margin: 0 0 0.2rem 0; }
    .brand-banner p { margin: 0; opacity: 0.9; font-size: 0.95rem; }

    .car-card {
        border: 1px solid #e3e6ea;
        border-radius: 16px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.8rem;
        background: #ffffff;
    }
    .car-card.selected {
        border: 2px solid #003876;
        background: #f3f7fc;
    }
    .price-row {
        display: flex;
        justify-content: space-between;
        padding: 0.45rem 0;
        border-bottom: 1px solid #eef0f2;
        font-size: 1.02rem;
    }
    .price-row.total {
        font-weight: 700;
        font-size: 1.15rem;
        border-bottom: none;
        padding-top: 0.7rem;
    }
    .badge {
        display: inline-block;
        background: #eaf2fb;
        color: #003876;
        border-radius: 999px;
        padding: 0.15rem 0.7rem;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .disclaimer {
        color: #8a8f98;
        font-size: 0.82rem;
        margin-top: 1.5rem;
        line-height: 1.4;
    }
    .color-legend-item {
        display: inline-flex;
        align-items: center;
        margin-right: 14px;
        font-size: 0.9rem;
        margin-bottom: 6px;
    }
    .color-swatch {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        border: 1px solid rgba(0,0,0,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------------------------
defaults = {
    "step": 0,
    "q_sub": 0,
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


# ---------------------------------------------------------------------------
# 공통 컴포넌트
# ---------------------------------------------------------------------------
def header():
    st.markdown(
        """
        <div class="brand-banner">
            <h1>🚗 나에게 맞는 차량 찾기</h1>
            <p>우리금융캐피탈과 함께, 내 취향에 꼭 맞는 차량과 금융조건을 찾아보세요</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(main_step_idx):
    total = len(STEP_LABELS)
    st.progress((main_step_idx + 1) / total)
    cols = st.columns(total)
    for i, label in enumerate(STEP_LABELS):
        style = "font-weight:700;color:#003876;" if i == main_step_idx else "color:#a3a8b0;"
        cols[i].markdown(f"<div style='text-align:center;font-size:0.78rem;{style}'>{label}</div>",
                          unsafe_allow_html=True)
    st.write("")


def option_grid(options, state_key, columns=2):
    selected = st.session_state.get(state_key)
    cols = st.columns(columns)
    for i, opt in enumerate(options):
        col = cols[i % columns]
        is_sel = selected == i
        label = ("✅  " if is_sel else "") + opt
        if col.button(label, key=f"{state_key}_opt_{i}", type="primary" if is_sel else "secondary",
                      use_container_width=True):
            st.session_state[state_key] = i
            st.rerun()


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
        '<circle cx="118" cy="164" r="26" fill="#1c1c1c"/>',
        '<circle cx="118" cy="164" r="11" fill="#9aa0a6"/>',
        '<circle cx="288" cy="164" r="26" fill="#1c1c1c"/>',
        '<circle cx="288" cy="164" r="11" fill="#9aa0a6"/>',
        '</svg>',
    ]
    return "".join(parts)


def _image_data_uri(path: str) -> str:
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "jpeg" if ext == "jpg" else ext
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:image/{mime};base64,{b64}"


IMAGE_EXTS = ("jpg", "jpeg", "png", "webp", "avif")


def render_car_image(car_id: str, color: dict):
    """assets/cars/<car_id>/<color_id>.(jpg|jpeg|png|webp|avif) 파일이 있으면 해당 색상 실제 이미지를 그대로,
    없으면 그 차량의 대표 사진(photo.*)에 선택한 색상을 합성해서, 그마저 없으면 자리표시 이미지를 보여준다."""
    for ext in IMAGE_EXTS:
        path = os.path.join(ASSETS_DIR, car_id, f"{color['id']}.{ext}")
        if os.path.exists(path):
            uri = _image_data_uri(path)
            st.markdown(f'<img src="{uri}" style="width:100%;display:block;border-radius:18px;">',
                        unsafe_allow_html=True)
            return
    for ext in IMAGE_EXTS:
        path = os.path.join(ASSETS_DIR, car_id, f"photo.{ext}")
        if os.path.exists(path):
            uri = _image_data_uri(path)
            html = (
                '<div style="position:relative;border-radius:18px;overflow:hidden;">'
                f'<img src="{uri}" style="width:100%;display:block;">'
                f'<div style="position:absolute;inset:0;background:{color["hex"]};'
                'opacity:0.4;mix-blend-mode:color;"></div>'
                '<div style="position:absolute;top:14px;left:14px;display:flex;align-items:center;'
                'gap:8px;background:rgba(255,255,255,0.92);padding:6px 14px 6px 6px;border-radius:999px;'
                'box-shadow:0 2px 10px rgba(0,0,0,0.25);">'
                f'<span style="width:26px;height:26px;border-radius:50%;background:{color["hex"]};'
                'display:inline-block;border:2px solid white;box-shadow:0 0 0 1px rgba(0,0,0,0.15);"></span>'
                f'<span style="font-size:0.85rem;font-weight:700;color:#222;">{color["name"]}</span>'
                "</div>"
                "</div>"
            )
            st.markdown(html, unsafe_allow_html=True)
            st.caption("* 예시 사진에 선택하신 색상을 합성한 이미지이며, 실제 색상과 다를 수 있습니다.")
            return
    svg = car_placeholder_svg(color["hex"])
    html = f'<div style="background:#f5f7fa;border-radius:18px;padding:1.2rem;">{svg}</div>'
    st.markdown(html, unsafe_allow_html=True)


def price_breakdown_card(car, used_price):
    principal = max(car["price"] - used_price, 0)
    st.markdown('<div class="car-card">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="price-row"><span>신차 가격 (원가)</span><span>{data.fmt_10k(car['price'])}</span></div>
        <div class="price-row"><span>보유 차량 보상판매가 (−)</span><span>-{data.fmt_10k(used_price)}</span></div>
        <div class="price-row total"><span>실 부담 금액</span><span>{data.fmt_10k(principal)}</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    return principal


def disclaimer():
    st.markdown(
        """<div class="disclaimer">
        * 본 서비스는 전시·체험용 데모이며, 표시되는 차량 가격·중고차 시세·금리·월 납부금은 임의로 산정된 예시 값입니다.<br/>
        실제 시세 및 금융조건은 우리금융캐피탈 상담을 통해 정확히 확인하시기 바랍니다.
        </div>""",
        unsafe_allow_html=True,
    )


def send_consultation_email(payload: dict):
    """상담 신청 내용을 이메일로 발송한다. Streamlit Secrets(GMAIL_USER, GMAIL_APP_PASSWORD)가
    설정되어 있어야 동작하며, 없으면 (False, 안내 메시지)를 반환한다."""
    try:
        gmail_user = st.secrets["GMAIL_USER"]
        gmail_pass = st.secrets["GMAIL_APP_PASSWORD"]
        recipient = st.secrets.get("RECIPIENT_EMAIL", gmail_user)
    except Exception:
        return False, "이메일 발송 기능이 아직 설정되지 않았습니다. (관리자: Streamlit Secrets에 GMAIL_USER / GMAIL_APP_PASSWORD 설정 필요)"

    body = "\n".join([
        f"신청자: {payload['name']} ({payload['phone']})",
        "",
        f"관심 차량: {payload['car_brand']} {payload['car_model']} - {payload['color_name']}",
        f"트림: {payload['trim_name']} / 휠: {payload['wheel_name']}",
        f"금융조건: {payload['finance_name']} · {payload['term']}개월",
        f"총 차량 가격: {payload['total_price']}",
        f"예상 월 납부금: {payload['monthly']}",
        "",
        f"하차예정(보유) 차량: {payload['used_brand']} {payload['used_model']} ({payload['used_year']}년)",
        f"예상 보상판매가: {payload['used_price']}",
    ])
    msg = MIMEText(body)
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
# STEP 0: 인트로
# ---------------------------------------------------------------------------
def render_intro():
    header()
    st.markdown("### 👋 환영합니다")
    st.write(
        "내 차량 정보와 취향, 그리고 원하는 금융조건을 알려주시면 "
        "우리금융캐피탈이 꼭 맞는 차량과 합리적인 월 납부금을 추천해 드립니다."
    )
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.markdown("**1️⃣ 보유 차량 선택**\n\n브랜드·차종·연식")
    c2.markdown("**2️⃣ 취향 질문 3가지**\n\n나에게 맞는 차량 매칭")
    c3.markdown("**3️⃣ 금융조건 선택**\n\n할부 · 리스 · 렌트")
    st.write("")
    if st.button("시작하기 →", type="primary", use_container_width=True):
        go(1)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 1: 보유 차량 선택
# ---------------------------------------------------------------------------
def render_used_car():
    header()
    progress_bar(0)
    st.markdown("#### 🚙 현재 보유 중인 차량을 선택해 주세요")

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

    st.session_state.used_brand = brand
    st.session_state.used_model = model
    st.session_state.used_year = year

    used_price = data.get_used_price(brand, model, year)
    segment = data.USED_CAR_DB[brand][model]["segment"]
    st.info(f"**{brand} {model} ({year}년, {segment})** 예상 보상판매가 **{data.fmt_10k(used_price)}**")

    st.write("")
    c1, c2 = st.columns([1, 3])
    if c1.button("← 처음으로", use_container_width=True):
        go(0)
    if c2.button("다음 →", type="primary", use_container_width=True):
        go(2)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 2: 취향 질문 (3문항)
# ---------------------------------------------------------------------------
def render_taste():
    header()
    progress_bar(1)

    q_sub = st.session_state.q_sub
    q = data.QUESTIONS[q_sub]
    st.markdown(f"##### 질문 {q_sub + 1} / 3")
    st.markdown(f"#### {q['title']}")
    st.write("")
    option_grid(q["options"], q["key"], columns=2)
    st.write("")

    c1, c2 = st.columns([1, 3])
    if q_sub == 0:
        if c1.button("← 이전 단계", use_container_width=True):
            go(1)
    else:
        if c1.button("← 이전 질문", use_container_width=True):
            st.session_state.q_sub -= 1
            st.rerun()

    answered = st.session_state.get(q["key"]) is not None
    next_label = "다음 질문 →" if q_sub < 2 else "취향 분석 결과 보기 →"
    if c2.button(next_label, type="primary", use_container_width=True, disabled=not answered):
        if q_sub < 2:
            st.session_state.q_sub += 1
            st.rerun()
        else:
            go(3)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 3: 금융조건 선택
# ---------------------------------------------------------------------------
def render_finance():
    header()
    progress_bar(2)
    st.markdown("#### 💳 원하시는 금융조건을 선택해 주세요")
    st.caption("카드를 누르면 바로 선택됩니다")
    st.write("")

    for opt in data.FINANCE_OPTIONS:
        is_sel = st.session_state.finance_id == opt["id"]
        check = " ✅" if is_sel else ""
        label = f"{opt['icon']} **{opt['name']}**{check} — {opt['summary']}\n\n{opt['desc']}"
        if st.button(label, key=f"fin_{opt['id']}", type="primary" if is_sel else "secondary",
                     use_container_width=True):
            st.session_state.finance_id = opt["id"]
            st.rerun()
        st.write("")

    st.write("")
    c1, c2 = st.columns([1, 3])
    if c1.button("← 이전 단계", use_container_width=True):
        go(2, q_sub=2)
    if c2.button("추천 결과 보기 →", type="primary", use_container_width=True,
                 disabled=st.session_state.finance_id is None):
        go(4)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 4: 추천 결과
# ---------------------------------------------------------------------------
def render_result():
    header()
    progress_bar(3)

    recs = data.recommend_cars(st.session_state.q1, st.session_state.q2, st.session_state.q3, top_n=3)
    if st.session_state.selected_car_id not in [c["id"] for c in recs]:
        st.session_state.selected_car_id = recs[0]["id"]

    used_price = data.get_used_price(st.session_state.used_brand, st.session_state.used_model,
                                      st.session_state.used_year)

    st.markdown("#### ✨ 취향 분석 결과, 이런 차량을 추천드려요")
    st.caption("카드를 눌러 추천 차량을 바꿔볼 수 있어요")

    for i, car in enumerate(recs):
        is_sel = st.session_state.selected_car_id == car["id"]
        badge = "🏆 BEST MATCH" if i == 0 else f"추천 {i + 1}"
        check = " ✅" if is_sel else ""
        label = (f"{badge}{check}\n\n"
                 f"**{car['brand']} {car['model']}** · {car['segment']} · {data.fmt_10k(car['price'])}\n\n"
                 f"{car['tagline']}")
        if st.button(label, key=f"pick_{car['id']}", type="primary" if is_sel else "secondary",
                     use_container_width=True):
            st.session_state.selected_car_id = car["id"]
            st.rerun()
        st.write("")

    selected_car = data.get_car_by_id(st.session_state.selected_car_id)

    st.write("")
    st.markdown("#### 💰 예상 가격 및 월 납부금")
    principal = price_breakdown_card(selected_car, used_price)

    term = st.select_slider("약정 기간", options=[24, 36, 48, 60, 72], value=st.session_state.term_months,
                             format_func=lambda m: f"{m}개월")
    st.session_state.term_months = term

    monthly = data.calc_monthly_payment(st.session_state.finance_id, principal, selected_car["price"], term)
    finance_name = next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == st.session_state.finance_id)

    st.markdown(
        f"""
        <div class="car-card selected" style="text-align:center;">
            <div style="font-size:0.95rem;color:#555;">{finance_name} · {term}개월 기준 예상 월 납부금</div>
            <div style="font-size:2.1rem;font-weight:800;color:#003876;">월 {data.fmt_10k(monthly)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2 = st.columns([1, 3])
    if c1.button("← 이전 단계", use_container_width=True):
        go(3)
    if c2.button("🚗 차량 만나보기 →", type="primary", use_container_width=True):
        go(5)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 5: 차량 상세 / 옵션(색상) 선택
# ---------------------------------------------------------------------------
def render_detail():
    header()
    progress_bar(4)

    car = data.get_car_by_id(st.session_state.selected_car_id)
    if car is None:
        go(4)
        return

    st.markdown(f"#### 🚗 {car['brand']} {car['model']}")
    st.caption(car["desc"])

    with st.expander("🔁 추천 차량 · 금융조건 다시 선택하기"):
        recs = data.recommend_cars(st.session_state.q1, st.session_state.q2, st.session_state.q3, top_n=3)
        st.markdown("**추천 차량**")
        rcols = st.columns(3)
        for i, rc in enumerate(recs):
            is_sel = st.session_state.selected_car_id == rc["id"]
            label = f"{rc['brand']} {rc['model']}" + (" ✅" if is_sel else "")
            if rcols[i].button(label, key=f"detail_pick_{rc['id']}",
                                type="primary" if is_sel else "secondary", use_container_width=True):
                if st.session_state.selected_car_id != rc["id"]:
                    st.session_state.selected_car_id = rc["id"]
                    st.session_state.selected_color_idx = 0
                    st.session_state.selected_trim_id = "standard"
                    st.session_state.selected_wheel_id = "18in"
                    st.rerun()

        st.markdown("**금융조건**")
        fcols = st.columns(3)
        for i, fo in enumerate(data.FINANCE_OPTIONS):
            is_sel = st.session_state.finance_id == fo["id"]
            label = f"{fo['icon']} {fo['name']}" + (" ✅" if is_sel else "")
            if fcols[i].button(label, key=f"detail_fin_{fo['id']}",
                                type="primary" if is_sel else "secondary", use_container_width=True):
                st.session_state.finance_id = fo["id"]
                st.rerun()

    colors = car["colors"]
    color_names = [c["name"] for c in colors]
    idx = min(st.session_state.selected_color_idx, len(colors) - 1)

    legend_html = "".join(
        f'<span class="color-legend-item"><span class="color-swatch" '
        f'style="background:{c["hex"]}"></span>{c["name"]}</span>'
        for c in colors
    )
    st.markdown(legend_html, unsafe_allow_html=True)

    chosen_name = st.radio("색상 선택", color_names, index=idx, horizontal=True, label_visibility="collapsed")
    st.session_state.selected_color_idx = color_names.index(chosen_name)
    color = colors[st.session_state.selected_color_idx]

    render_car_image(car["id"], color)
    st.markdown(f"<div style='text-align:center;margin-top:0.5rem;font-weight:600;'>{color['name']}</div>",
                unsafe_allow_html=True)

    st.write("")
    st.markdown("##### 트림 선택")
    trim_names = [t["name"] for t in data.TRIM_LEVELS]
    trim_idx = next((i for i, t in enumerate(data.TRIM_LEVELS) if t["id"] == st.session_state.selected_trim_id), 0)
    chosen_trim_name = st.radio("트림 선택", trim_names, index=trim_idx, horizontal=True,
                                 label_visibility="collapsed", key="trim_radio")
    trim = data.TRIM_LEVELS[trim_names.index(chosen_trim_name)]
    st.session_state.selected_trim_id = trim["id"]
    delta_txt = f" (+{data.fmt_10k(trim['price_delta'])})" if trim["price_delta"] else " (기본 포함)"
    st.caption(f"{trim['desc']}{delta_txt}")

    st.markdown("##### 휠 선택")
    wheel_names = [w["name"] for w in data.WHEEL_OPTIONS]
    wheel_idx = next((i for i, w in enumerate(data.WHEEL_OPTIONS) if w["id"] == st.session_state.selected_wheel_id), 0)
    chosen_wheel_name = st.radio("휠 선택", wheel_names, index=wheel_idx, horizontal=True,
                                  label_visibility="collapsed", key="wheel_radio")
    wheel = data.WHEEL_OPTIONS[wheel_names.index(chosen_wheel_name)]
    st.session_state.selected_wheel_id = wheel["id"]

    st.write("")
    used_price = data.get_used_price(st.session_state.used_brand, st.session_state.used_model,
                                      st.session_state.used_year)
    total_price = car["price"] + trim["price_delta"] + wheel["price_delta"]
    principal = max(total_price - used_price, 0)
    monthly = data.calc_monthly_payment(st.session_state.finance_id, principal, total_price,
                                         st.session_state.term_months)
    finance_name = next(f["name"] for f in data.FINANCE_OPTIONS if f["id"] == st.session_state.finance_id)
    st.markdown(
        f"""
        <div class="car-card">
            <div class="price-row"><span>차량 기본가</span><span>{data.fmt_10k(car['price'])}</span></div>
            <div class="price-row"><span>트림 · 휠 추가금</span><span>+{data.fmt_10k(trim['price_delta'] + wheel['price_delta'])}</span></div>
            <div class="price-row"><span>총 차량 가격</span><span>{data.fmt_10k(total_price)}</span></div>
            <div class="price-row"><span>보유 차량 보상판매가 (−)</span><span>-{data.fmt_10k(used_price)}</span></div>
            <div class="price-row"><span>실 부담 금액</span><span>{data.fmt_10k(principal)}</span></div>
            <div class="price-row"><span>금융조건</span><span>{finance_name} · {st.session_state.term_months}개월</span></div>
            <div class="price-row total"><span>예상 월 납부금</span><span>월 {data.fmt_10k(monthly)}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.markdown("##### 📩 상담 신청하기")
    with st.form("consult_form", clear_on_submit=True):
        name = st.text_input("이름")
        phone = st.text_input("연락처 (휴대폰 번호)", placeholder="010-0000-0000")
        submitted = st.form_submit_button("상담 신청하기", type="primary", use_container_width=True)
        if submitted:
            if not name.strip() or not phone.strip():
                st.warning("이름과 연락처를 입력해 주세요.")
            else:
                payload = {
                    "name": name.strip(),
                    "phone": phone.strip(),
                    "car_brand": car["brand"],
                    "car_model": car["model"],
                    "color_name": color["name"],
                    "trim_name": trim["name"],
                    "wheel_name": wheel["name"],
                    "finance_name": finance_name,
                    "term": st.session_state.term_months,
                    "total_price": data.fmt_10k(total_price),
                    "monthly": f"월 {data.fmt_10k(monthly)}",
                    "used_brand": st.session_state.used_brand,
                    "used_model": st.session_state.used_model,
                    "used_year": st.session_state.used_year,
                    "used_price": data.fmt_10k(used_price),
                }
                ok, result_msg = send_consultation_email(payload)
                if ok:
                    st.success(result_msg)
                else:
                    st.error(result_msg)

    if st.button("← 추천 결과로", use_container_width=True):
        go(4)

    st.write("")
    if st.button("🔁 처음부터 다시 하기", use_container_width=True):
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
