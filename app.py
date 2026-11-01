# -*- coding: utf-8 -*-
"""
우리금융캐피탈 - 내 차에서 드림카까지 (체험형 데모)
"""
import base64
import html
import json
import os
import smtplib
import urllib.parse
import urllib.request
from datetime import datetime
from email.mime.text import MIMEText

import streamlit as st
import streamlit.components.v1 as components

import importlib

import data

data = importlib.reload(data)   # 배포 직후 data.py 가 이전 버전으로 캐시돼 있어도 항상 최신 값을 쓰도록 한다

st.set_page_config(page_title="나에게 맞는 차량 찾기 | 우리금융캐피탈", page_icon=":material/directions_car:", layout="wide")

# 이모지 대신 쓰는 라인 아이콘 (currentColor 로 색이 따라간다)
_ICON_PATHS = {
    "car": '<path d="M4 16.5v-4l1.8-5A2 2 0 0 1 7.7 6h8.6a2 2 0 0 1 1.9 1.5l1.8 5v4"/><path d="M3 16.5h18"/>'
           '<path d="M6 16.5V19M18 16.5V19"/><circle cx="7.6" cy="13" r=".7"/><circle cx="16.4" cy="13" r=".7"/>',
    "key": '<circle cx="8" cy="12" r="3.6"/><path d="M11.6 12H21M17.5 12v3M20.5 12v2"/>',
    "spark": '<path d="M11 3.5l1.7 5L18 10l-5.3 1.5L11 16.5l-1.7-5L4 10l5.3-1.5z"/><path d="M18.5 15.5l.6 1.8 1.9.6-1.9.6-.6 1.8-.6-1.8-1.9-.6 1.9-.6z"/>',
    "wallet": '<rect x="3" y="6" width="18" height="13" rx="3"/><path d="M3 10.5h18"/><circle cx="16.8" cy="14.8" r="1"/>',
    "swap": '<path d="M5 8.5h13.5l-3-3M19 15.5H5.5l3 3"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
}
FIN_ICON = {"installment": "wallet", "lease": "swap", "rent": "calendar"}


# 상단 로고 마크: 부장님 서비스(dream.webp)와 같은 톤(은은한 블루·민트 배경 + 실버/라이트블루 소프트 차량)의 벡터 일러스트.
# 직접 만든 이미지를 쓰려면 assets/brand/logo.png (또는 jpg/webp) 를 넣으면 자동으로 이 일러스트 대신 쓰인다.
_BRAND_SVG = (
    '<svg viewBox="5 16 54 36" xmlns="http://www.w3.org/2000/svg" aria-label="드림카">'
    '<defs>'
    '<linearGradient id="bgm" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cfe9ff"/><stop offset="1" stop-color="#d3f5e9"/></linearGradient>'
    '<linearGradient id="bdy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f7f9fc"/><stop offset="1" stop-color="#bfcbdb"/></linearGradient>'
    '<linearGradient id="gls" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d7eeff"/><stop offset="1" stop-color="#7fbdf0"/></linearGradient>'
    '</defs>'
    '<rect x="0" y="0" width="64" height="64" fill="url(#bgm)"/>'
    '<path d="M-4 52 C14 40 40 38 70 46 L70 70 L-4 70Z" fill="#ffffff" opacity=".5"/>'
    '<ellipse cx="32" cy="48.5" rx="23" ry="3.2" fill="#2b5f8f" opacity=".18"/>'
    '<path d="M16.5 34 L21.5 24.6 Q22.6 22.8 24.7 22.8 H38.4 Q40.5 22.8 41.9 24.4 L48 34Z" fill="url(#bdy)"/>'
    '<path d="M21.3 33 L25 26 H31 V33Z" fill="url(#gls)"/>'
    '<path d="M33 26 H38 Q39 26 39.7 26.9 L44.2 33 H33Z" fill="url(#gls)"/>'
    '<rect x="8" y="32.5" width="49" height="12" rx="6" fill="url(#bdy)"/>'
    '<rect x="10" y="40.2" width="45" height="3.4" rx="1.7" fill="#7cc4f5"/>'
    '<ellipse cx="54.4" cy="37" rx="2.3" ry="1.7" fill="#fff4b8"/>'
    '<circle cx="19.5" cy="43.8" r="5.6" fill="#33445c"/><circle cx="19.5" cy="43.8" r="3" fill="#e9eff7"/>'
    '<circle cx="45.5" cy="43.8" r="5.6" fill="#33445c"/><circle cx="45.5" cy="43.8" r="3" fill="#e9eff7"/>'
    '</svg>'
)


def brand_mark() -> str:
    brand_dir = os.path.join(os.path.dirname(__file__), "assets", "brand")
    for ext in IMAGE_EXTS:
        path = os.path.join(brand_dir, f"logo.{ext}")
        if os.path.exists(path):
            return f'<img src="{_image_data_uri(path)}" alt="드림카">'
    return _BRAND_SVG


def ico(name: str, size: int = 22) -> str:
    return (f'<svg class="ico" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{_ICON_PATHS[name]}</svg>')

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "cars")
IMAGE_EXTS = ("jpg", "jpeg", "png", "webp", "avif")
DOMESTIC_BRANDS = {"현대", "기아", "제네시스", "쉐보레", "KG모빌리티", "르노코리아"}
IMPORT_BRANDS = {"BMW", "벤츠", "아우디", "폭스바겐", "토요타", "렉서스", "볼보", "미니"}

# ---------------------------------------------------------------------------
# 스타일 (AI LAB 메인 + STOCK:ON 페이지의 다크 글래스 스타일)
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.css');
:root{--bg:#f3f6fb;--surface:#ffffff;--surface-2:#eef3fa;--border:#dbe3ef;
--text:#14213a;--text-muted:#566380;--text-subtle:#8792ab;
--accent:#0067ac;--accent-strong:#004f86;--accent-soft:rgba(0,103,172,.09);--accent-line:rgba(0,103,172,.38);
--sel:#0067ac;--sel-glow:rgba(0,103,172,.16);--shadow:0 6px 22px rgba(20,40,80,.07);
--mint:#0e9a69;--mint-ink:#0a7a54;--mint-soft:rgba(14,154,105,.10);--mint-line:rgba(14,154,105,.38);
--violet:#6d4fd8;--amber:#d98a00;--rose:#e11d48;--tint:#cfe8fb;}
.stApp :is(p,span,div,label,button,h1,h2,h3,h4,h5,li,input,textarea,a,td,th):not([data-testid="stIconMaterial"]){
  font-family:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans KR",sans-serif;
  word-break:keep-all;}
.stApp{background:radial-gradient(900px 420px at 50% -8%,rgba(0,103,172,.13),transparent 70%),
  radial-gradient(560px 340px at 108% 30%,rgba(26,143,214,.07),transparent 70%),var(--bg);color:var(--text);}
header[data-testid="stHeader"],#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
.block-container{max-width:900px;padding:1.2rem 1rem 4rem;}
@keyframes dcUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.dc-hero,.dc-dark,.dc-card,.dc-top3,.dc-how>div,.dc-fleet>div,.dc-tblwrap{animation:dcUp .45s ease both;}

/* 상단 바 / 히어로 / STEP 탭 */
.dc-top{display:flex;align-items:center;justify-content:space-between;margin:4px 2px 18px;}
.dc-logo{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;letter-spacing:-.01em;color:var(--text);}
.dc-logo i{width:44px;height:44px;border-radius:14px;overflow:hidden;background:linear-gradient(135deg,#dff0ff,#d7f6ec);
  display:inline-flex;align-items:center;justify-content:center;font-style:normal;border:1px solid #cfe3f5;box-shadow:0 6px 16px rgba(0,103,172,.18);}
.dc-logo i svg,.dc-logo i img{width:100%;height:100%;display:block;object-fit:cover;object-position:42% 55%;}
.dc-logo em{font-style:normal;color:var(--accent);}
.dc-brand{text-align:right;}
.dc-proto{display:inline-block;border:1px solid rgba(217,138,0,.55);color:#8a5a00;background:rgba(251,191,36,.18);
  padding:2px 10px;border-radius:999px;font-size:.7rem;font-weight:800;letter-spacing:.12em;margin-left:8px;vertical-align:middle;}
.dc-brand .dc-proto{display:block;width:max-content;margin:4px 0 0 auto;}
.dc-hero{--tint:#cfe8fb;position:relative;overflow:hidden;border-radius:28px;padding:34px 36px 28px;color:#fff;margin-bottom:16px;
  background:radial-gradient(circle at 90% -5%,rgba(120,205,255,.55),transparent 46%),
  linear-gradient(135deg,#00376a 0%,#0067ac 60%,#1a8fd6 125%);
  box-shadow:0 20px 44px rgba(0,80,140,.30);}
.dc-kick{display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.12);
  border-radius:999px;padding:7px 14px;font-size:12.5px;letter-spacing:.14em;font-weight:800;color:#fff;}
.dc-kick:before{content:"";width:7px;height:7px;border-radius:50%;background:#ffd166;display:inline-block;}
.dc-hero h1.t{color:#fff;font-size:2.4rem;line-height:1.25;font-weight:800;margin:18px 0 14px;padding:0;position:relative;z-index:1;}
.dc-hero h1.t em{font-style:normal;color:#ffd166;}
.dc-hero p{color:rgba(255,255,255,.9);font-size:1rem;line-height:1.7;margin:0;max-width:580px;position:relative;z-index:1;}
.dc-tags{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:16px;max-width:520px;position:relative;z-index:1;}
.dc-tags span{border:1px solid rgba(255,255,255,.26);background:rgba(255,255,255,.11);border-radius:999px;padding:5px 4px;font-size:.76rem;font-weight:700;color:#fff;text-align:center;white-space:nowrap;}
.dc-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:26px;padding-top:22px;border-top:1px solid rgba(255,255,255,.22);position:relative;z-index:1;}
.dc-stats b{display:block;font-size:1.9rem;font-weight:800;color:#fff;line-height:1.1;}
.dc-stats span{display:block;font-size:.82rem;color:var(--tint);margin-top:4px;font-weight:600;}
.dc-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(104px,1fr));gap:8px;margin-bottom:22px;
  background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:6px;box-shadow:var(--shadow);}
.dc-chip{border-radius:13px;padding:10px 6px;text-align:center;background:var(--mint-soft);color:var(--mint-ink);}
.dc-chip b{display:block;font-size:.82rem;font-weight:800;letter-spacing:.06em;}
.dc-chip span{display:block;font-size:.8rem;font-weight:600;margin-top:2px;}
.dc-chip.todo{background:transparent;color:var(--text-subtle);}
.dc-chip.now{background:var(--accent-soft);color:var(--accent-strong);box-shadow:inset 0 0 0 1.5px var(--accent);}

/* 이동 가능한 STEP 탭 (모바일에서도 한 줄 유지) */
.st-key-dcsteps{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:6px;margin-bottom:22px;box-shadow:var(--shadow);}
.st-key-dcsteps [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:6px!important;}
.st-key-dcsteps [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important;width:auto!important;}
.st-key-dcsteps [data-testid="stMarkdownContainer"],.st-key-dcsteps [data-testid="stMarkdown"]{margin-bottom:0!important;}
[class*="st-key-card_nav"]{margin-bottom:0!important;}
.dc-chip .sh{display:none;}
.dc-chip.done{cursor:pointer;transition:all .15s ease;}
[class*="st-key-card_nav"]:hover .dc-chip.done{background:rgba(14,154,105,.2);color:#065f46;}
[class*="st-key-card_nav"]:hover .dc-card{transform:none;}

/* 카드 (흰 카드 + 블루 선택 테두리) */
.dc-card{background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:22px 24px;transition:all .15s ease;box-shadow:var(--shadow);}
.dc-card.sel{border-color:var(--sel);box-shadow:0 0 0 1px var(--sel),0 8px 26px var(--sel-glow);}
.dc-card .tt{font-size:1.12rem;font-weight:800;color:var(--text);}
.dc-card .ds{font-size:.92rem;color:var(--text-muted);margin-top:6px;line-height:1.55;}
.dc-card .go{font-size:.85rem;font-weight:800;color:var(--accent);margin-top:12px;}
.dc-card.fork{min-height:0;display:grid;grid-template-columns:auto 1fr;column-gap:14px;align-items:start;padding:18px 20px;}
.dc-card .ic{margin-bottom:12px;}
.dc-card.fork .ic{width:54px;height:54px;border-radius:17px;background:var(--accent-soft);border:1px solid var(--accent-line);
  color:var(--accent);display:flex;align-items:center;justify-content:center;}
.dc-card.fork .ic{grid-row:1 / span 3;width:46px;height:46px;border-radius:14px;margin:0;}
.dc-card.fork .go{margin-top:8px;}
svg.ico{display:block;}
.dc-card.cmp .nm svg.ico{display:inline-block;vertical-align:-3px;margin-right:5px;color:var(--accent);}
.dc-fleet .im svg.ico{opacity:.7;}
.dc-logo i svg.ico{margin:0;}
.dc-card.fin{display:flex;gap:16px;align-items:flex-start;}
.dc-card.fin .ic{margin:0;width:52px;height:52px;border-radius:16px;background:var(--accent-soft);border:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;font-size:1.6rem;flex:none;}
.dc-card.fin .sm{font-size:.88rem;font-weight:600;color:var(--text-muted);margin-left:8px;}
.dc-tagrow{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px;}
.dc-tagrow span{background:var(--surface-2);border:1px solid var(--border);color:var(--text);border-radius:999px;padding:3px 10px;font-size:.76rem;font-weight:700;}
.dc-card.opt{display:flex;gap:14px;align-items:flex-start;min-height:104px;}
.dc-card.opt .lt{width:34px;height:34px;border-radius:11px;background:var(--accent-soft);border:1px solid var(--accent-line);color:var(--accent);
  display:flex;align-items:center;justify-content:center;font-weight:800;flex:none;}
.dc-card.opt.sel .lt{background:var(--accent);border-color:var(--accent);color:#fff;}
.dc-card.cmp{text-align:center;padding:18px 14px;}
.dc-card.cmp .nm{font-weight:800;font-size:.95rem;color:var(--text-muted);}
.dc-card.cmp .mo{font-size:1.9rem;font-weight:800;color:var(--text);margin-top:6px;line-height:1.15;}
.dc-card.cmp .mo small{font-size:.95rem;font-weight:700;color:var(--text-muted);}
.dc-card.cmp .sb{font-size:.78rem;color:var(--text-subtle);margin-top:4px;}
[class*="st-key-card_"]{position:relative;margin-bottom:12px;}
[class*="st-key-card_"] [data-testid="stMarkdown"],[class*="st-key-card_"] [data-testid="stMarkdownContainer"]{margin-bottom:0!important;}
[class*="st-key-card_"] [data-testid="stElementContainer"]:has(button){position:absolute!important;inset:0!important;
  width:100%!important;height:100%!important;z-index:5;margin:0!important;}
[class*="st-key-card_"] [data-testid="stButton"]{width:100%!important;height:100%!important;}
[class*="st-key-card_"] [data-testid="stButton"] button{width:100%!important;height:100%!important;opacity:0;
  min-height:0!important;padding:0!important;cursor:pointer;}
[class*="st-key-card_"]:hover .dc-card,[class*="st-key-card_"]:hover .dc-top3{border-color:var(--accent-line);transform:translateY(-2px);}
[class*="st-key-card_"]:hover .dc-card.sel,[class*="st-key-card_"]:hover .dc-top3.sel{border-color:var(--sel);}

/* 섹션 제목 / 진행 점 */
.dc-eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:var(--accent);text-transform:uppercase;}
.dc-ebrow{display:flex;justify-content:space-between;align-items:center;margin-top:6px;}
.dc-pill-s{background:var(--accent-soft);color:var(--accent-strong);font-weight:800;font-size:.85rem;padding:5px 12px;border-radius:999px;border:1px solid var(--accent-line);}
h2.dc-h2{font-size:1.45rem;font-weight:800;margin:6px 0 6px;padding:0;color:var(--text);}
p.dc-sub{color:var(--text-muted);font-size:.95rem;margin:0 0 14px;line-height:1.6;}
p.dc-note{color:var(--text-subtle);font-size:.82rem;margin:4px 0 0;}
.dc-lbl{font-weight:800;font-size:.92rem;color:var(--text);margin:14px 0 6px;}
.dc-finex{margin:12px 2px 4px;padding:2px 0 2px 12px;border-left:3px solid #bcd3e6;color:var(--text-subtle);font-size:.84rem;line-height:1.6;}
.dc-finex b{color:var(--text-muted);font-weight:800;}
.dc-consent{font-size:.84rem;line-height:1.6;color:var(--text-muted);margin:0 0 10px;}
.dc-consent b{color:var(--text);}
.dc-finex span{display:block;margin-top:2px;}
.dc-sec{margin:26px 0 4px;}
.dc-dots{display:flex;gap:6px;margin:4px 0 12px;}
.dc-dots i{height:6px;flex:1;border-radius:99px;background:#d9e1ee;}
.dc-dots i.on{background:linear-gradient(90deg,#0067ac,#38b6ff);}
.dc-answers{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px;}
.dc-answers span{background:var(--mint-soft);border:1px solid var(--mint-line);border-radius:999px;padding:5px 12px;font-size:.8rem;font-weight:700;color:var(--mint-ink);}

/* 시작 화면: 진행 안내 / 차량 미리보기 */
.dc-how{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:8px;}
.dc-how>div{background:var(--surface);border:1px solid var(--border);border-radius:20px;padding:16px;box-shadow:var(--shadow);}
.dc-how em{font-style:normal;font-weight:800;color:var(--accent);font-size:.8rem;letter-spacing:.1em;}
.dc-how b{display:block;margin-top:6px;font-size:.98rem;color:var(--text);}
.dc-how span{display:block;margin-top:4px;font-size:.82rem;color:var(--text-muted);line-height:1.5;}
.dc-fleet{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:8px;}
.dc-fleet>div{background:var(--surface);border:1px solid var(--border);border-radius:20px;overflow:hidden;box-shadow:var(--shadow);}
.dc-fleet .im{background:#eef3fa;height:90px;display:flex;align-items:center;justify-content:center;}
.dc-fleet .im img{width:100%;height:100%;object-fit:contain;}
.dc-fleet .bd{padding:10px 12px 12px;}
.dc-fleet .bd b{display:block;font-size:.9rem;color:var(--text);}
.dc-fleet .bd span{font-size:.78rem;color:var(--text-muted);}

/* 색이 다른 강조 카드: 기본(우리 블루) / 페르소나(인디고) / 견적(딥 틸) / 내 차 시세(네이비) */
.dc-dark{--tint:#cfe8fb;border-radius:28px;color:#fff;padding:26px 28px;
  box-shadow:0 20px 44px rgba(0,60,110,.28);margin:6px 0 10px;
  background:radial-gradient(circle at 90% -10%,rgba(120,205,255,.5),transparent 48%),linear-gradient(135deg,#00376a 0%,#0067ac 60%,#1a8fd6 125%);}
.dc-dark.pers{--tint:#ddd6fe;box-shadow:0 20px 44px rgba(50,40,140,.28);
  background:radial-gradient(circle at 90% -10%,rgba(167,139,250,.55),transparent 48%),
  linear-gradient(135deg,#1b1a5c 0%,#33359f 60%,#5b55d6 125%);}
.dc-dark.dc-quote{--tint:#b9ecf2;box-shadow:0 20px 44px rgba(0,80,100,.28);
  background:radial-gradient(circle at 90% -10%,rgba(80,220,230,.42),transparent 48%),
  linear-gradient(135deg,#032b45 0%,#07607c 60%,#0b9aa0 125%);}
.dc-dark.val{--tint:#cfe0f7;box-shadow:0 20px 44px rgba(20,40,90,.28);
  background:radial-gradient(circle at 90% -10%,rgba(150,180,255,.4),transparent 48%),
  linear-gradient(135deg,#101d3f 0%,#1f3a73 60%,#3a62b0 125%);}
.dc-dark .dc-eb{color:var(--tint);}
.dc-persona{display:flex;gap:26px;align-items:center;}
.dc-persona .im{width:200px;height:170px;border-radius:20px;background:#f1f4f9;flex:none;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.dc-persona .im img{width:100%;height:100%;object-fit:contain;}
.dc-persona .eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:var(--tint);}
.dc-persona h3{color:#fff;font-size:1.9rem;font-weight:800;margin:6px 0 4px;padding:0;}
.dc-persona .sb{font-weight:800;font-size:1.02rem;margin-bottom:8px;color:#fff;}
.dc-persona .ds{color:rgba(255,255,255,.88);font-size:.95rem;line-height:1.6;}
.dc-persona .qt{color:var(--tint);font-style:italic;margin-top:10px;font-size:.95rem;}

/* TOP 카드 / 비교표 / 일치도 막대 */
.dc-top3{background:var(--surface);border:1px solid var(--border);border-radius:24px;overflow:hidden;transition:all .15s ease;box-shadow:var(--shadow);}
.dc-top3.sel{border-color:var(--sel);box-shadow:0 0 0 1px var(--sel),0 8px 26px var(--sel-glow);}
.dc-top3 .im{background:#eef3fa;height:138px;display:flex;align-items:center;justify-content:center;}
.dc-top3 .im img{width:100%;height:100%;object-fit:contain;}
.dc-top3 .bd{padding:14px 16px 16px;}
.dc-top3 .tg{font-size:.78rem;font-weight:800;color:var(--accent);letter-spacing:.06em;}
.dc-top3 .rw{display:flex;justify-content:space-between;align-items:baseline;gap:8px;}
.dc-top3 .nm{font-size:1.08rem;font-weight:800;margin-top:2px;color:var(--text);}
.dc-top3 .mt{font-size:1.2rem;font-weight:800;color:var(--mint);}
.dc-top3 .ds{font-size:.82rem;color:var(--text-muted);margin:4px 0 8px;line-height:1.45;min-height:2.4em;}
.dc-top3 .pr{font-size:.85rem;color:var(--text-muted);font-weight:600;}
.dc-tblwrap{overflow-x:auto;background:var(--surface);border:1px solid var(--border);border-radius:20px;box-shadow:var(--shadow);}
table.dc-tbl{width:100%;border-collapse:collapse;min-width:760px;}
table.dc-tbl th,table.dc-tbl td{padding:12px 14px;text-align:center;font-size:.9rem;border-bottom:1px solid var(--border);color:var(--text);}
table.dc-tbl th{font-weight:800;color:var(--text);background:#f3f6fb;}
table.dc-tbl td:first-child,table.dc-tbl th:first-child{text-align:left;color:var(--text-muted);font-weight:700;}
table.dc-tbl tr:last-child td{border-bottom:none;}
table.dc-tbl .hl{background:var(--accent-soft);}
.dc-bars{margin-top:12px;display:grid;gap:12px;}
.dc-bar .lb{display:flex;justify-content:space-between;font-size:.88rem;font-weight:700;color:var(--text-muted);margin-bottom:5px;}
.dc-bar .lb b{color:var(--text);}
.dc-bar .tr{height:9px;border-radius:99px;background:#e1e8f3;overflow:hidden;}
.dc-bar .tr i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#0067ac,#38b6ff);}

/* 추천 설명 */
.dc-why{font-size:1rem;line-height:1.75;color:var(--text);}
.dc-ai{display:inline-block;background:rgba(109,79,216,.10);color:#5b3fc4;font-weight:800;font-size:.75rem;padding:3px 10px;border-radius:999px;margin-left:8px;border:1px solid rgba(109,79,216,.4);}

/* 견적 카드 */
.dc-quote .top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;}
.dc-quote .eb{font-size:12.5px;letter-spacing:.13em;font-weight:800;color:var(--tint);}
.dc-quote .sub{color:rgba(255,255,255,.9);margin-top:4px;font-size:.95rem;}
.dc-quote .big{font-size:2.7rem;font-weight:800;line-height:1.15;margin-top:2px;color:#fff;}
.dc-quote .big small{font-size:1.2rem;font-weight:700;}
.dc-chipw{background:rgba(255,255,255,.16);padding:8px 14px;border-radius:999px;font-weight:700;font-size:.88rem;border:1px solid rgba(255,255,255,.24);}
.dc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:18px;}
.dc-tile{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:12px 14px;}
.dc-tile span{display:block;font-size:.8rem;color:var(--tint);}
.dc-tile b{display:block;font-size:.98rem;margin-top:2px;color:#fff;}
.dc-quote .foot{font-size:.8rem;color:rgba(255,255,255,.75);margin-top:16px;}

/* 차량 상세 */
.dc-sumbar{display:flex;gap:8px;flex-wrap:wrap;margin:2px 0 14px;}
.dc-sumbar span{background:var(--surface);border:1px solid var(--border);border-radius:999px;padding:6px 13px;font-size:.82rem;font-weight:700;color:var(--text);}
.dc-sumbar span.hi{background:var(--accent-soft);border-color:var(--accent-line);color:var(--accent-strong);}
.dc-imgbox{background:#eef3fa;border:1px solid var(--border);border-radius:24px;padding:10px;box-shadow:var(--shadow);}
.dc-imgbox img{width:100%;display:block;border-radius:18px;}
.dc-swatch{display:inline-flex;align-items:center;margin-right:14px;font-size:.88rem;margin-bottom:6px;color:var(--text-muted);font-weight:600;}
.dc-swatch i{width:15px;height:15px;border-radius:50%;display:inline-block;margin-right:6px;border:1px solid rgba(20,33,58,.28);}

/* 세그먼트(pill 탭) */
div[data-testid="stRadio"] div[role="radiogroup"]{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:5px;gap:4px;flex-wrap:wrap;box-shadow:var(--shadow);}
div[data-testid="stRadio"] label[data-testid="stRadioOption"]{flex:1 1 auto;justify-content:center;padding:9px 14px;border-radius:12px;margin:0!important;cursor:pointer;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"]>div>div>div:first-child{display:none;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"] p{font-weight:700;color:var(--text-muted);font-size:.92rem;text-align:center;}
div[data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"]{background:var(--accent-soft);box-shadow:inset 0 0 0 1.5px var(--accent);}
div[data-testid="stRadio"] label[data-testid="stRadioOption"][data-selected="true"] p{color:var(--accent-strong);font-weight:800;}

/* 실시간 데이터 / 추천 이유 / 확장 후보 */
.dc-live{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;background:var(--surface);border:1px solid var(--border);
  border-radius:18px;padding:12px 16px;margin:0 0 18px;font-size:.88rem;color:var(--text-muted);box-shadow:var(--shadow);}
.dc-live .lv{display:inline-flex;align-items:center;gap:7px;font-weight:800;color:var(--mint-ink);letter-spacing:.08em;font-size:.76rem;}
.dc-live .lv:before{content:"";width:8px;height:8px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 0 rgba(14,154,105,.7);animation:dcPulse 1.8s infinite;}
@keyframes dcPulse{0%{box-shadow:0 0 0 0 rgba(14,154,105,.55)}70%{box-shadow:0 0 0 9px rgba(14,154,105,0)}100%{box-shadow:0 0 0 0 rgba(14,154,105,0)}}
.dc-live b{color:var(--text);}
.dc-live .idx{background:var(--mint-soft);border:1px solid var(--mint-line);color:var(--mint-ink);border-radius:999px;padding:3px 11px;font-weight:800;}
.dc-live .src{flex-basis:100%;font-size:.72rem;color:var(--text-subtle);}
.dc-whyi{display:flex;gap:12px;align-items:flex-start;padding:14px 0;border-top:1px solid var(--border);}
.dc-whyi:first-of-type{border-top:none;}
.dc-whyi .n{width:34px;height:34px;border-radius:11px;background:var(--accent-soft);border:1px solid var(--accent-line);color:var(--accent-strong);
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.8rem;flex:none;}
.dc-whyi .tx{flex:1;font-size:.95rem;line-height:1.6;color:var(--text);}
.dc-whyi .tx b{color:var(--text);}
.dc-whyi .need{color:var(--text-muted);font-size:.86rem;}
.dc-fit{display:inline-block;border-radius:999px;padding:2px 10px;font-size:.74rem;font-weight:800;margin-left:6px;vertical-align:middle;}
.dc-fit.f3{background:var(--mint-soft);color:var(--mint-ink);border:1px solid var(--mint-line);}
.dc-fit.f2{background:rgba(0,103,172,.09);color:var(--accent-strong);border:1px solid var(--accent-line);}
.dc-fit.f1{background:rgba(217,138,0,.12);color:#8a5a00;border:1px solid rgba(217,138,0,.4);}
.dc-fit.f0{background:rgba(225,29,72,.08);color:#be123c;border:1px solid rgba(225,29,72,.35);}
.dc-callout{border-radius:16px;padding:14px 16px;font-size:.92rem;line-height:1.6;margin-top:10px;background:rgba(217,138,0,.08);border:1px solid rgba(217,138,0,.35);color:#7a4e00;}
.dc-callout.blue{background:var(--surface);border:1px solid var(--border);border-left:3px solid var(--accent);color:var(--text);}
.dc-callout a{color:var(--accent);font-weight:800;text-decoration:underline;}
.dc-axes{margin-top:14px;display:grid;grid-template-columns:repeat(2,1fr);gap:8px 18px;}
.dc-axes div .lb{display:flex;justify-content:space-between;font-size:.76rem;color:var(--tint);font-weight:700;margin-bottom:3px;}
.dc-axes div .tr{height:6px;border-radius:99px;background:rgba(255,255,255,.2);overflow:hidden;}
.dc-axes div .tr i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#c4b5fd,#f0abfc);}
.dc-kw{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px;}
.dc-kw span{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.22);border-radius:999px;padding:3px 11px;font-size:.78rem;font-weight:700;}
.im.ph{position:relative;flex-direction:column;background:linear-gradient(160deg,#f1f5fb,#dde6f3);}
.im.ph svg{width:70%;height:auto;opacity:.85;}
.im.ph span{position:absolute;bottom:6px;right:10px;font-size:.62rem;letter-spacing:.12em;font-weight:800;color:#8a97ae;}
.dc-card.row{display:flex;align-items:center;gap:14px;padding:14px 18px;}
.dc-card.row .rk{width:34px;height:34px;border-radius:11px;background:var(--accent-soft);border:1px solid var(--accent-line);display:flex;align-items:center;justify-content:center;font-weight:800;color:var(--accent);flex:none;}
.dc-card.row .nm{flex:1;font-weight:800;color:var(--text);font-size:.98rem;}
.dc-card.row .nm span{display:block;font-weight:600;font-size:.78rem;color:var(--text-muted);margin-top:2px;}
.dc-card.row .mt{font-weight:800;color:var(--mint);}
.dc-card.row .pr{font-size:.82rem;color:var(--text-muted);font-weight:700;min-width:70px;text-align:right;}
.dc-hc{display:flex;gap:18px;align-items:center;padding:16px;}
.dc-hc .im{width:230px;height:150px;flex:none;border-radius:18px;background:#eef3fa;display:flex;align-items:center;justify-content:center;overflow:hidden;}
.dc-hc .im img{width:100%;height:100%;object-fit:contain;}
.dc-hc .tx{flex:1;min-width:0;}
.dc-hc h3{font-size:1.5rem;font-weight:800;margin:4px 0;padding:0;color:var(--text);}
.dc-hc .ds{color:var(--text-muted);font-size:.92rem;line-height:1.5;}
.dc-hm{margin-top:10px;font-weight:800;color:var(--accent);font-size:1rem;}
.dc-hm b{font-size:2rem;letter-spacing:-.02em;margin:0 2px;}
.dc-hm span{display:block;font-size:.8rem;font-weight:600;color:var(--text-muted);margin-top:2px;}
.dc-valc{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 20px;margin-top:14px;}
.dc-valc .nm{font-size:.95rem;margin-top:4px;color:rgba(255,255,255,.92);font-weight:700;}
.dc-valc .rg{font-size:.76rem;margin-top:3px;color:rgba(255,255,255,.72);}
.dc-valc .pr{font-size:2rem;font-weight:800;line-height:1.1;white-space:nowrap;text-align:right;}
.dc-valc .pr small{font-size:.9rem;font-weight:700;}
.dc-plate{display:flex;align-items:stretch;width:max-content;max-width:100%;margin:14px auto 0;border:2.5px solid #1b2a41;border-radius:10px;background:#fff;overflow:hidden;box-shadow:0 2px 8px rgba(20,33,58,.12);}
.dc-plate i{width:20px;background:#0067ac;flex:none;}
.dc-plate span{padding:6px 22px;font-size:1.7rem;font-weight:800;letter-spacing:.06em;color:#1b2a41;line-height:1.2;white-space:nowrap;}
.st-key-plate_input input{font-size:1.15rem;font-weight:700;text-align:center;letter-spacing:.04em;}
.st-key-stickynav button:disabled{background:#dfe6f0!important;color:#8a97ab!important;box-shadow:none!important;border-color:transparent!important;}
[data-testid="stLayoutWrapper"]:has(> .st-key-stickynav){position:sticky;bottom:0;z-index:30;}
.st-key-stickynav{padding:10px 0 calc(10px + env(safe-area-inset-bottom,0px));
  background:linear-gradient(180deg,rgba(243,246,251,0),rgba(243,246,251,.96) 28%);backdrop-filter:blur(6px);}
.st-key-stickynav [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:8px!important;}
.st-key-stickynav [data-testid="stColumn"]{min-width:0!important;}
.dc-rankbox{padding:8px 20px 16px;}
.dc-rank{display:flex;align-items:center;gap:12px;padding:11px 0;border-bottom:1px solid var(--border);}
.dc-rank .rk{width:28px;height:28px;border-radius:9px;background:var(--surface-2);color:var(--text-muted);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.85rem;flex:none;}
.dc-rank .rk.top{background:var(--accent);color:#fff;}
.dc-rank .bd{flex:1;min-width:0;}
.dc-rank .lb{display:flex;justify-content:space-between;gap:8px;font-size:.92rem;margin-bottom:5px;}
.dc-rank .lb b{color:var(--text);} .dc-rank .lb span{color:var(--text-muted);font-weight:700;}
.dc-rank .tr{height:7px;border-radius:99px;background:#e1e8f3;overflow:hidden;}
.dc-rank .tr i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#0067ac,#38b6ff);}
.dc-rankbox .src{font-size:.72rem;color:var(--text-subtle);margin-top:12px;line-height:1.5;}
.dc-rankbox .src a{color:var(--accent);font-weight:700;}
.dc-hint{font-size:.78rem;color:var(--text-subtle);margin:2px 0 8px;text-align:right;}
div[data-testid="stElementContainer"]:has(iframe){position:absolute!important;height:0!important;overflow:hidden;margin:0!important;opacity:0;}
.st-key-top5row [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;overflow-x:auto;scroll-snap-type:x mandatory;gap:12px!important;padding-bottom:8px;-webkit-overflow-scrolling:touch;}
.st-key-top5row [data-testid="stColumn"]{flex:0 0 270px!important;min-width:270px!important;scroll-snap-align:start;}
table.dc-tbl td:first-child,table.dc-tbl th:first-child{position:sticky;left:0;background:#fff;z-index:1;}
table.dc-tbl th:first-child{background:#f3f6fb;}

/* 버튼 */
div.stButton>button,div[data-testid="stFormSubmitButton"]>button{border-radius:14px;border:1px solid var(--border);
  background:var(--surface);color:var(--text);font-weight:700;min-height:3.1rem;box-shadow:var(--shadow);}
div.stButton>button:hover{border-color:var(--accent);color:var(--accent);}
div.stButton>button[data-testid="stBaseButton-primary"],div[data-testid="stFormSubmitButton"]>button[data-testid="stBaseButton-primaryFormSubmit"]{
  background:linear-gradient(135deg,#1a8fd6,#0067ac);border-color:#0067ac;color:#fff;box-shadow:0 8px 22px rgba(0,103,172,.30);}
div.stButton>button[data-testid="stBaseButton-primary"]:hover{color:#fff;filter:brightness(1.06);}
div[data-testid="stExpander"]{background:var(--surface);border:1px solid var(--border)!important;border-radius:18px;}
div[data-testid="stForm"]{background:var(--surface);border:1px solid var(--border);border-radius:20px;}
.dc-disclaimer{color:var(--text-subtle);font-size:.8rem;line-height:1.55;margin-top:22px;text-align:center;}

@media (max-width:640px){
  .dc-chip .fl{display:none;} .dc-chip .sh{display:block;}
  .dc-chip{padding:8px 2px;} .dc-chip b{font-size:.66rem;letter-spacing:.02em;} .dc-chip span{font-size:.72rem;margin-top:1px;}
  .st-key-dcsteps{padding:4px;} .st-key-dcsteps [data-testid="stHorizontalBlock"]{gap:4px!important;}
  .st-key-top5row [data-testid="stColumn"]{flex:0 0 76%!important;min-width:76%!important;}
  .st-key-cmprow [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:8px!important;}
  .st-key-cmprow [data-testid="stColumn"]{min-width:0!important;flex:1 1 0!important;}
  .dc-axes{grid-template-columns:1fr 1fr;} .dc-live{font-size:.82rem;}
  .dc-card.cmp{padding:14px 6px;} .dc-card.cmp .mo{font-size:1.25rem;} .dc-card.cmp .mo small{font-size:.7rem;display:block;}
  .dc-card.fork{min-height:0;} .dc-card.opt{min-height:0;padding:16px 16px;}
  .block-container{padding:.8rem .75rem 4rem;}
  h2.dc-h2{font-size:1.25rem;}
  .dc-hc{flex-direction:column;align-items:stretch;} .dc-hc .im{width:100%;height:135px;}
  .dc-hero{padding:24px 20px 20px;} .dc-hero h1.t{font-size:1.55rem;margin:14px 0 10px;} .dc-hero p{font-size:.92rem;line-height:1.6;}
  .dc-tags{grid-template-columns:repeat(2,1fr);} .dc-tags span{padding:6px 4px;font-size:.74rem;}
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
    "car_confirmed": False,
    "used_plate": "",
    "plate_input": "",
    "used_km": None,
    "used_brand": None,
    "used_model": None,
    "used_year": None,
    "q1": None,
    "q2": None,
    "q3": None,
    "finance_id": "lease",
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
def scroll_to_top_on_page_change():
    """단계(또는 질문)가 바뀌면 화면을 맨 위로 올린다. 바뀌지 않은 재실행(선택 변경 등)에서는 위치를 유지한다."""
    page_key = (st.session_state.step, st.session_state.q_sub)
    if st.session_state.get("_last_page") != page_key:
        st.session_state["_last_page"] = page_key
        st.session_state["_scroll_nonce"] = st.session_state.get("_scroll_nonce", 0) + 1
        # 새 화면이 그려지는 동안 위치가 다시 밀릴 수 있어, 몇 번에 걸쳐 맨 위로 올린다.
        script = (
            "function up(){try{var d=window.parent.document;var a=d.getElementById('dc-top');"
            "if(a){a.scrollIntoView({block:'start'});}"
            "var m=d.querySelector('[data-testid=\"stMain\"]');if(m){m.scrollTo(0,0);}"
            "window.parent.scrollTo(0,0);"
            "try{window.parent.parent.scrollTo(0,0);}catch(e){}}catch(e){}}"
            "up();setTimeout(up,120);setTimeout(up,400);setTimeout(up,900);"
        )
        page = f"<!-- nav {st.session_state['_scroll_nonce']} --><script>{script}</script>"
        if hasattr(st, "iframe"):   # components.v1.html 은 제거 예정이라 최신 Streamlit 에서는 st.iframe 을 쓴다
            st.iframe(page, height=1)
        else:
            components.html(page, height=0)


def topbar():
    scroll_to_top_on_page_change()
    st.markdown(
        '<div id="dc-top"></div><div class="dc-top"><div class="dc-logo"><i>' + brand_mark() + '</i><span>드림<em>:</em>Car</span></div>'
        '<div class="dc-brand"><span class="dc-proto">PROTOTYPE</span></div></div>',
        unsafe_allow_html=True,
    )


def reachable(app_step: int) -> bool:
    """해당 단계에 필요한 데이터가 이미 있어서 이동 가능한지."""
    ss = st.session_state
    answered = all(ss[k] is not None for k in ("q1", "q2", "q3"))
    if app_step == 1:
        return ss.has_car is True
    started = ss.has_car is False or (ss.has_car is True and ss.car_confirmed)
    if app_step == 2:
        return started
    if app_step == 4:
        return started and answered
    if app_step == 5:
        return reachable(4)
    return False


# 앱 단계 번호 → (긴 이름, 짧은 이름). 3번(금융 선택)은 결과 화면 안으로 합쳤다.
STEP_LABELS = {1: ("내 차 가치 확인", "내 차"), 2: ("라이프스타일 분석", "취향"),
               4: ("드림카 추천·견적", "추천·견적"), 5: ("차량 만나보기", "만나보기")}


def step_chips(step_idx: int):
    """step_idx: 앱 단계(0=시작, 1=보유차량, 2=취향, 4=추천·견적, 5=만나보기).
    시작 화면은 안내용 표시만, 그 외 화면은 이동 가능한 단계(데이터가 이미 있는 단계)를 눌러서 이동할 수 있다."""
    app_steps = [1, 2, 4, 5]
    if st.session_state.has_car is False:
        app_steps = [2, 4, 5]

    def chip_html(pos, a, cls):
        return (f'<div class="dc-chip {cls}"><b>STEP {pos + 1:02d}</b>'
                f'<span class="fl">{STEP_LABELS[a][0]}</span><span class="sh">{STEP_LABELS[a][1]}</span></div>')

    if step_idx <= 0:
        st.markdown('<div class="dc-steps">' + "".join(chip_html(i, a, "") for i, a in enumerate(app_steps)) + "</div>",
                    unsafe_allow_html=True)
        return
    with st.container(key="dcsteps"):
        cols = st.columns(len(app_steps))
        for i, a in enumerate(app_steps):
            with cols[i]:
                if a == step_idx:
                    st.markdown(chip_html(i, a, "now"), unsafe_allow_html=True)
                elif reachable(a):
                    if card_button(f"nav_{a}", chip_html(i, a, "done")):
                        go(a)
                else:
                    st.markdown(chip_html(i, a, "todo"), unsafe_allow_html=True)


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
    # 값이 바깥에서 바뀌었거나 위젯이 처음 그려질 때만 위젯 값을 맞춘다.
    # (매번 덮어쓰면 사용자가 방금 누른 선택이 무시된다)
    sync_key = widget_key + "__synced"
    if widget_key not in st.session_state or st.session_state.get(sync_key) != cur:
        st.session_state[widget_key] = cur
        st.session_state[sync_key] = cur
    val = st.radio(label, options, format_func=fmt, horizontal=True, key=widget_key,
                   label_visibility="collapsed")
    if val != cur:
        st.session_state[state_key] = val
        st.session_state[sync_key] = val
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
def sales_ranking_html() -> str:
    """이번 달 판매 순위 (data.SALES_RANKING 을 매월 갱신)."""
    sr = data.SALES_RANKING
    top = max(n for _, n in sr["items"])
    rows = []
    for i, (name, n) in enumerate(sr["items"], 1):
        rows.append(f'<div class="dc-rank"><span class="rk{" top" if i <= 3 else ""}">{i}</span>'
                    f'<div class="bd"><div class="lb"><b>{name}</b><span>{n:,}대</span></div>'
                    f'<div class="tr"><i style="width:{n / top * 100:.0f}%"></i></div></div></div>')
    return ('<div class="dc-card dc-rankbox">' + "".join(rows)
            + f'<div class="src">{sr["period"]} {sr["title"]} · 출처 <a href="{sr["url"]}" target="_blank" rel="noopener">{sr["source"]}</a>'
              f' · 매월 갱신 · 집계 기준에 따라 수치가 다를 수 있어요</div></div>')


def thumb(car: dict) -> str:
    uri = car_rep_uri(car)
    if uri:
        return f'<div class="im"><img src="{uri}"></div>'
    return f'<div class="im ph">{car_placeholder_svg("#8fa0ba")}<span>PHOTO SOON</span></div>'


def reason_items(car: dict, q1: int, q2: int, q3: int):
    rows = []
    scores = [car["scores"][("q1", "q2", "q3")[qi]][idx] for qi, idx in enumerate((q1, q2, q3))]
    best_trait = car["traits"][scores.index(max(scores))]
    for qi, idx in enumerate((q1, q2, q3)):
        sc = scores[qi]
        if sc >= 2:
            trait = car["traits"][qi]
        else:
            # 이 항목이 약하면 억지로 끼워 맞추지 않고, 대신 가장 강한 점을 보여준다.
            trait = f"이 항목은 이 차의 가장 큰 강점은 아니에요. 대신 {best_trait}이(가) 취향과 잘 맞아요"
        rows.append({
            "n": f"Q{qi + 1}", "answer": data.QUESTIONS[qi]["options"][idx], "need": data.ANSWER_NEEDS[qi][idx],
            "trait": trait, "score": sc, "label": data.FIT_LABELS[sc],
        })
    return rows


FINANCE_NOTES = {
    "installment": "내 명의로 소유하고 주행거리 제한 없이 탈 수 있는 방식이에요.",
    "lease": "월 부담을 낮추고, 만기 때 인수·반납·교체 중에서 고를 수 있는 방식이에요.",
    "rent": "보험·정비 서비스를 포함하고 초기 부담이 적어 부담 없이 시작하는 방식이에요.",
}


def finance_story(car: dict, quotes: dict) -> str:
    cur = st.session_state.finance_id
    fit = data.finance_fit(car, cur)
    low_id = min(quotes, key=lambda k: quotes[k]["monthly"])
    txt = (f"지금 선택하신 <b>{finance_name(cur)}</b>은 월 <b>{quotes[cur]['monthly']:,.1f}만원</b>이에요. "
           f"{FINANCE_NOTES[cur]} ")
    if low_id != cur:
        diff = quotes[cur]["monthly"] - quotes[low_id]["monthly"]
        txt += f"월 납부금만 보면 <b>{finance_name(low_id)}</b>이 {diff:,.1f}만원 더 낮아요. "
    else:
        txt += "세 방식 중 월 납부금이 가장 낮아요. "
    if fit >= 0.6:
        txt += "이 차량은 일반적으로 이 방식과 궁합이 좋은 편이에요."
    return txt


# ---------------------------------------------------------------------------
# 차량 이미지 (계속)
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
    if has_car:
        tiles = [
            ("신차가격", data.fmt_10k(q["total"])),
            ("내 차 시세", data.fmt_10k(q["used"])),
            ("원금 (차량가−시세)", data.fmt_10k(q["principal"])),
            ("약정기간", f"{q['term']}개월"),
            ("현재 차량", car_txt),
            ("금융조건", finance_name()),
        ]
    else:   # 보유 차량이 없으면 시세·현재 차량 항목 자체를 보여주지 않는다 (원금 = 차량가)
        tiles = [
            ("원금 (신차가격)", data.fmt_10k(q["principal"])),
            ("약정기간", f"{q['term']}개월"),
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
        f"선택한 금융조건: {fin}\n"
        f"차량 강점: {' / '.join(car['traits'])}\n"
        f"참고할 점: {car['watch']}"
    )
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": (
                "당신은 우리금융캐피탈 체험존의 자동차 추천 도우미입니다. 고객의 취향 답변을 근거로 이 차량이 왜 어울리는지 "
                "한국어로 4~5문장, 친근하고 구체적으로 설명하세요. 고객이 고른 답변 3가지를 각각 짚어 주세요. 가격·금리·승인 가능 여부를 단정하거나 약속하지 말고, "
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
        f"개인정보 수집·이용 동의: 동의함 ({payload.get('consent_at', '-')})",
        "",
        f"관심 차량: {payload['car_brand']} {payload['car_model']} - {payload['color_name']}",
        f"트림: {payload['trim_name']} / 휠: {payload['wheel_name']}",
        f"금융조건: {payload['finance_name']} · {payload['term']}개월",
        f"총 차량 가격: {payload['total_price']}",
    ]
    if payload["has_car"]:
        lines += [
            f"차량번호: {payload.get('used_plate') or '-'} (체험용 임의 조회값)",
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
    st.markdown(
        '<div class="dc-hero"><div class="dc-kick">MY CAR CHANGE JOURNEY</div>'
        '<h1 class="t">지금 타는 차에서,<br><em>다음 드림카까지.</em></h1>'
        '<p>3가지 질문으로 나에게 맞는 차를 추천받고, 내 차 시세를 반영한 월 납부금까지 1분 만에 확인하세요.</p></div>',
        unsafe_allow_html=True,
    )
    section("START", "지금 타고 계신 차가 있으신가요?",
            "차가 있으면 시세를 원금에서 빼 드리고, 없어도 바로 추천받을 수 있어요.")
    c1, c2 = st.columns(2)
    with c1:
        if card_button("fork_has", '<div class="dc-card fork"><div class="ic">' + ico("key", 26) + '</div><div class="tt">내 차가 있어요</div>'
                                   '<div class="ds">차량번호만 입력하면 예상 중고차 시세를 확인하고, 그만큼 원금에서 빼서 견적을 받아요</div>'
                                   '<div class="go">내 차 시세 확인하기 →</div></div>'):
            st.session_state.has_car = True
            go(1)
    with c2:
        if card_button("fork_none", '<div class="dc-card fork"><div class="ic">' + ico("spark", 26) + '</div><div class="tt">차량이 없어요</div>'
                                    '<div class="ds">바로 취향을 알려주고 새 차를 추천받아요. 원금은 차량가 전액으로 계산돼요</div>'
                                    '<div class="go">드림카 바로 찾기 →</div></div>'):
            st.session_state.has_car = False
            st.session_state.used_plate = ""
            st.session_state.plate_input = ""
            st.session_state.used_km = None
            st.session_state.used_brand = None
            st.session_state.used_model = None
            st.session_state.used_year = None
            go(2)

    section("BEST SELLERS", "요즘 가장 많이 팔린 차는?", data.SALES_RANKING["subtitle"], cls="dc-sec")
    st.markdown(sales_ranking_html(), unsafe_allow_html=True)
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 1: 내 차 가치 확인
# ---------------------------------------------------------------------------
@st.dialog("차량번호 확인")
def plate_error_dialog():
    st.markdown("**차량번호를 정확히 입력해 주세요.**")
    st.caption("예) 12가 3456 · 123나 4567 (띄어쓰기는 있어도 없어도 돼요)")
    if st.button("확인", type="primary", use_container_width=True):
        st.rerun()


def render_used_car():
    page_head(1)
    section("STEP 01 · MY CAR VALUE", "차량번호를 입력해 주세요",
            "번호만 넣으면 내 차의 예상 중고차 판매가를 바로 확인해 드려요.")

    # 다른 단계에 다녀온 뒤에도 입력값을 유지하고, 조회된 번호는 띄어쓰기 없이 입력했어도 표준 표기로 보여준다
    if st.session_state.used_plate and (not st.session_state.plate_input
                                        or data.parse_plate(st.session_state.plate_input) == st.session_state.used_plate):
        st.session_state.plate_input = st.session_state.used_plate
    with st.form("plate_form", border=False):
        plate_in = st.text_input("차량번호", max_chars=12, key="plate_input",
                                 placeholder="예) 12가 3456", label_visibility="collapsed")
        looked = st.form_submit_button("내 차 조회하기", type="primary", use_container_width=True)
    if looked:
        plate = data.parse_plate(plate_in)
        if plate:
            r = data.lookup_by_plate(plate)
            ss = st.session_state
            ss.used_plate = plate
            ss.used_brand, ss.used_model, ss.used_year, ss.used_km = r["brand"], r["model"], r["year"], r["km"]
            st.rerun()
        else:
            plate_error_dialog()

    ss = st.session_state
    found = bool(ss.used_plate and ss.used_brand)
    if found:
        brand, model, year = ss.used_brand, ss.used_model, ss.used_year
        info = data.USED_CAR_DB[brand][model]
        used_price = data.get_used_price(brand, model, year)
        retain = round(100 * used_price / info["new_price"])
        lo, hi = round(used_price * 0.95), round(used_price * 1.05)
        st.markdown(
            f'<div class="dc-plate"><i></i><span>{html.escape(ss.used_plate)}</span></div>'
            '<div class="dc-dark val dc-valc"><div class="l"><div class="dc-eb" style="color:var(--tint);">MY CAR VALUE</div>'
            f'<div class="nm">{brand} {model} · {year}년식</div>'
            f'<div class="rg">약 {ss.used_km:,}km · 예상 범위 {lo:,}~{hi:,}만원 · 잔존가치 {retain}%</div></div>'
            f'<div class="pr">{used_price:,}<small> 만원</small></div></div>'
            '<p class="dc-note" style="margin-bottom:84px;">체험용 예상 시세예요. 예상 중고차 판매가는 신차 견적에서 원금으로 차감돼요.</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<p class="dc-note" style="margin-bottom:84px;">조회 결과는 체험용 예상값이며, 실제 차량 정보와 다를 수 있어요.</p>',
                    unsafe_allow_html=True)
    # 결과를 보면서도 다음 버튼이 항상 보이도록 하단에 고정
    with st.container(key="stickynav"):
        n1, n2 = st.columns([1, 2])
        if n1.button("← 처음으로", use_container_width=True):
            go(0)
        if n2.button("취향 선택하기 →", type="primary", use_container_width=True, disabled=not found):
            st.session_state.car_confirmed = True
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
    for pair in range(0, len(q["options"]), 2):
        cols = st.columns(2)   # 행 단위로 만들어야 휴대폰(세로 쌓임)에서도 A→B→C→D 순서가 유지된다
        for j in range(2):
            i = pair + j
            opt = q["options"][i]
            with cols[j]:
                sel = " sel" if selected == i else ""
                html = (f'<div class="dc-card opt{sel}"><div class="lt">{"ABCD"[i]}</div><div>'
                        f'<div class="tt">{opt}</div><div class="ds">{descs[i]}</div></div></div>')
                if card_button(f"q{q_sub}_{i}", html):
                    st.session_state[q["key"]] = i
                    if q_sub < 2:
                        st.session_state.q_sub += 1
                        st.rerun()
                    else:
                        go(4)

    if st.button("← 이전", use_container_width=True):
        if q_sub == 0:
            go(1 if st.session_state.has_car else 0)
        else:
            st.session_state.q_sub -= 1
            st.rerun()
    disclaimer()


# ---------------------------------------------------------------------------
# STEP 4: 추천 결과 + 견적
# ---------------------------------------------------------------------------
def render_result():
    page_head(4)
    q1, q2, q3 = st.session_state.q1, st.session_state.q2, st.session_state.q3
    ranked = data.rank_cars(q1, q2, q3)          # 금융조건을 바꿔도 추천 순서는 그대로
    top5, more = ranked[:5], ranked[5:10]
    rank_of = {c["id"]: i + 1 for i, c in enumerate(ranked)}
    if st.session_state.selected_car_id not in [c["id"] for c in ranked[:10]]:
        st.session_state.selected_car_id = top5[0]["id"]

    # 1) 추천 차량: 후보 선택 → 대표 카드
    section("YOUR DREAM CAR", "당신에게 가장 잘 맞는 드림카", "취향 3가지와 가장 가까운 순서예요. 다른 후보도 눌러서 바로 비교해 보세요.")
    pool = [c["id"] for c in top5]
    if st.session_state.selected_car_id not in pool:
        pool.append(st.session_state.selected_car_id)
    seg(pool, "selected_car_id", f"w_res_car_{len(pool)}",
        fmt=lambda i: f'{rank_of[i]}위 {data.get_car_by_id(i)["model"]}', label="추천 후보")
    car = data.get_car_by_id(st.session_state.selected_car_id)

    specs = "".join(f"<span>{x}</span>" for x in (car["segment"], car["fuel"], car["seats"], data.fmt_10k(car["price"])))
    hq = build_quote(car["price"])
    st.markdown(
        '<div class="dc-card dc-hc" style="margin-top:12px;">' + thumb(car) + '<div class="tx">'
        f'<div class="dc-eb">TOP {rank_of[car["id"]]} · 취향 매칭 {data.match_percent(car, q1, q2, q3)}%</div>'
        f'<h3>{car["brand"]} {car["model"]}</h3><div class="ds">{car["tagline"]}</div>'
        f'<div class="dc-hm">월 <b>{hq["monthly"]:,.1f}</b>만원<span>{finance_name()} · {hq["term"]}개월 · 원금 {data.fmt_10k(hq["principal"])}</span></div>'
        f'<div class="dc-tagrow">{specs}</div></div></div>',
        unsafe_allow_html=True,
    )

    # 2) 월 납부금: 금융조건 3종 → 약정기간 → 견적
    section("MONTHLY PAYMENT", "월 납부금", "금융조건을 누르면 견적이 바로 바뀌어요.", cls="dc-sec")
    fquotes = {fo["id"]: build_quote(car["price"], fo["id"]) for fo in data.FINANCE_OPTIONS}
    fcols = st.container(key="cmprow").columns(3)
    for i, fo in enumerate(data.FINANCE_OPTIONS):
        sel = " sel" if st.session_state.finance_id == fo["id"] else ""
        html = (f'<div class="dc-card cmp{sel}"><div class="nm">{ico(FIN_ICON.get(fo["id"], "wallet"), 16)}{fo["name"]}</div>'
                f'<div class="mo">{fquotes[fo["id"]]["monthly"]:,.1f}<small>만원/월</small></div>'
                f'<div class="sb">{st.session_state.term_months}개월 기준</div></div>')
        with fcols[i]:
            if card_button(f"cmp_{fo['id']}", html):
                st.session_state.finance_id = fo["id"]
                st.rerun()
    cur_fo = next(f for f in data.FINANCE_OPTIONS if f["id"] == st.session_state.finance_id)
    st.markdown(f'<div class="dc-finex"><b>{cur_fo["name"]}란?</b> {cur_fo["concept"]}<br>'
                f'<span>{cur_fo["diff"]}</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="dc-lbl">약정기간</div>', unsafe_allow_html=True)
    seg([24, 36, 48, 60, 72], "term_months", "w_res_term", fmt=lambda m: f"{m}개월", label="약정기간")
    quote_card(build_quote(car["price"]))

    if st.button("색상·옵션 고르고 상담 신청하기 →", type="primary", use_container_width=True):
        go(5)

    # 3) 추천 이유
    section("WHY THIS CAR", f"{car['model']}, 이래서 추천해요", "", cls="dc-sec")
    with st.spinner("추천 이유를 정리하고 있어요…"):
        text, is_ai = recommendation_text(car)
    badge = '<span class="dc-ai">AI 추천 설명</span>' if is_ai else ""
    items = "".join(
        f'<div class="dc-whyi"><div class="n">{r["n"]}</div><div class="tx"><b>‘{r["answer"]}’</b>'
        f'<span class="dc-fit f{r["score"]}">{r["label"]}</span>'
        f'<div class="need">{r["need"]}을(를) 원하셨어요</div>→ {r["trait"]}</div></div>'
        for r in reason_items(car, q1, q2, q3))
    st.markdown(
        '<div class="dc-card"><div class="dc-ebrow"><span class="dc-eb">추천 근거 3가지' + badge + '</span></div>'
        f'<div class="dc-why" style="margin-top:8px;">{text}</div>'
        + ('<p class="dc-note">※ AI가 작성한 설명이며 실제 상품 조건과 다를 수 있어요.</p>' if is_ai else "")
        + f'<div style="margin-top:8px;">{items}</div></div>',
        unsafe_allow_html=True,
    )

    # 4) 더 보기 (비교표 · 6~10위 · 참고)
    with st.expander("다른 후보와 더 비교해 보기"):
        head = "".join(f'<th class="{"hl" if rc["id"] == car["id"] else ""}">{rc["model"]}</th>' for rc in top5)
        qs = [build_quote(rc["price"]) for rc in top5]

        def row(label, vals):
            cells = "".join(f'<td class="{"hl" if rc["id"] == car["id"] else ""}">{v}</td>' for rc, v in zip(top5, vals))
            return f"<tr><td>{label}</td>{cells}</tr>"

        table = (
            '<div class="dc-tblwrap"><table class="dc-tbl"><tr><th></th>' + head + "</tr>"
            + row("차급", [rc["segment"] for rc in top5])
            + row("연료 · 승차", [f'{rc["fuel"]} · {rc["seats"]}' for rc in top5])
            + row("차량가", [data.fmt_10k(rc["price"]) for rc in top5])
            + row("원금", [data.fmt_10k(x["principal"]) for x in qs])
            + row("월 납부금", [f'<b>{x["monthly"]:,.1f}만원</b>' for x in qs])
            + row("취향 매칭률", [f'{data.match_percent(rc, q1, q2, q3)}%' for rc in top5])
            + "</table></div>"
        )
        st.markdown(table, unsafe_allow_html=True)
        st.markdown('<div class="dc-hint">표는 옆으로 넘길 수 있어요 →</div>', unsafe_allow_html=True)
        st.markdown('<div class="dc-lbl">6~10위 후보</div>', unsafe_allow_html=True)
        for rc in more:
            sel = " sel" if rc["id"] == car["id"] else ""
            html = (f'<div class="dc-card row{sel}"><div class="rk">{rank_of[rc["id"]]}</div>'
                    f'<div class="nm">{rc["brand"]} {rc["model"]}<span>{rc["segment"]} · {rc["fuel"]} · {rc["seats"]}</span></div>'
                    f'<div class="mt">{data.match_percent(rc, q1, q2, q3)}%</div><div class="pr">{data.fmt_10k(rc["price"])}</div></div>')
            if card_button(f"more_{rc['id']}", html):
                st.session_state.selected_car_id = rc["id"]
                st.rerun()
        news = "https://search.naver.com/search.naver?where=news&query=" + urllib.parse.quote(f"{car['model']} 신차")
        st.markdown(f'<div class="dc-callout"><b>이런 점은 참고하세요</b><br>{car["watch"]}</div>'
                    f'<div class="dc-callout blue">{car["model"]}의 최신 소식이 궁금하다면 '
                    f'<a href="{news}" target="_blank" rel="noopener">최신 뉴스 검색 ↗</a></div>',
                    unsafe_allow_html=True)

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
    q1, q2, q3 = st.session_state.q1, st.session_state.q2, st.session_state.q3
    top_ids = [r["id"] for r in data.rank_cars(q1, q2, q3)[:10]]
    if st.session_state.selected_car_id not in top_ids:
        st.session_state.selected_car_id = top_ids[0]
    car = data.get_car_by_id(st.session_state.selected_car_id)
    if st.session_state.get("last_detail_car") != car["id"]:
        st.session_state.last_detail_car = car["id"]
        st.session_state.selected_color_idx = 0

    section("MEET YOUR DREAM CAR", f"{car['brand']} {car['model']}", car["desc"])

    with st.expander("추천 차량 · 금융조건 다시 선택하기"):
        recs = data.rank_cars(q1, q2, q3)[:5]
        if st.session_state.selected_car_id not in [r["id"] for r in recs]:
            recs = recs + [data.get_car_by_id(st.session_state.selected_car_id)]
        st.markdown('<div class="dc-lbl">추천 차량 (TOP 5)</div>', unsafe_allow_html=True)
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
    if st.session_state.pop("_consult_clear", False):   # 접수에 성공했을 때만 입력칸을 비운다 (오류 시에는 입력값 유지)
        st.session_state.update({"c_name": "", "c_phone": "", "c_agree": False})
    with st.form("consult_form"):
        name = st.text_input("이름", key="c_name")
        phone = st.text_input("연락처 (휴대폰 번호)", placeholder="010-0000-0000", key="c_phone")
        with st.expander(f"{data.PRIVACY_CONSENT_TITLE} 보기"):
            st.markdown("".join(f'<div class="dc-consent"><b>{i}. {t}</b><br>{b}</div>'
                                for i, (t, b) in enumerate(data.PRIVACY_CONSENT, 1))
                        + f'<p class="dc-note">{data.PRIVACY_CONSENT_NOTE}</p>', unsafe_allow_html=True)
        agreed = st.checkbox("[필수] 개인정보 수집·이용에 동의합니다.", key="c_agree")
        submitted = st.form_submit_button("동의하고 상담 신청하기", type="primary", use_container_width=True)
        if submitted:
            if not name.strip() or not phone.strip():
                st.warning("이름과 연락처를 입력해 주세요.")
            elif not agreed:
                st.warning("상담을 신청하려면 개인정보 수집·이용에 동의해 주세요.")
            else:
                payload = {
                    "name": name.strip(), "phone": phone.strip(),
                    "consent_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "car_brand": car["brand"], "car_model": car["model"], "color_name": color["name"],
                    "trim_name": trim["name"], "wheel_name": wheel["name"],
                    "finance_name": finance_name(), "term": q["term"],
                    "total_price": data.fmt_10k(total_price), "monthly": f"월 {data.fmt_10k(q['monthly'])}",
                    "has_car": bool(st.session_state.has_car),
                    "used_plate": st.session_state.used_plate,
                    "used_brand": st.session_state.used_brand, "used_model": st.session_state.used_model,
                    "used_year": st.session_state.used_year, "used_price": data.fmt_10k(q["used"]),
                    "principal": data.fmt_10k(q["principal"]),
                }
                ok, msg = send_consultation_email(payload)
                if ok:
                    st.session_state["_consult_clear"] = True
                    st.session_state["_consult_done"] = msg
                    st.rerun()
                st.error(msg)
    if st.session_state.get("_consult_done"):
        st.success(st.session_state.pop("_consult_done"))

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
    4: render_result,
    5: render_detail,
}

ROUTES[st.session_state.step]()
