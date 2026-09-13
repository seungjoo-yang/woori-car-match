# -*- coding: utf-8 -*-
"""
차량 매칭 체험 서비스 - 데이터 정의
모든 가격은 데모/체험용으로 임의 산정한 값이며 실제 시세/금융조건과 다를 수 있습니다.
금액 단위: 만원
"""

CURRENT_YEAR = 2026

# ---------------------------------------------------------------------------
# 1) 보유 차량(중고차) DB
#    brand -> model -> {new_price(만원), segment, dep_rate(연간 감가율), years(선택 가능 연식)}
# ---------------------------------------------------------------------------

USED_CAR_DB = {
    "현대": {
        "캐스퍼": {"new_price": 1450, "segment": "경차", "dep_rate": 0.86, "years": range(2022, 2026)},
        "아반떼": {"new_price": 1900, "segment": "준중형", "dep_rate": 0.84, "years": range(2016, 2026)},
        "쏘나타": {"new_price": 2600, "segment": "중형", "dep_rate": 0.83, "years": range(2016, 2026)},
        "그랜저": {"new_price": 3800, "segment": "준대형", "dep_rate": 0.84, "years": range(2016, 2026)},
        "투싼": {"new_price": 2900, "segment": "SUV", "dep_rate": 0.85, "years": range(2016, 2026)},
        "싼타페": {"new_price": 3500, "segment": "SUV", "dep_rate": 0.85, "years": range(2016, 2026)},
        "아이오닉5": {"new_price": 5200, "segment": "전기 SUV", "dep_rate": 0.80, "years": range(2021, 2026)},
    },
    "기아": {
        "레이": {"new_price": 1600, "segment": "경차", "dep_rate": 0.86, "years": range(2016, 2026)},
        "K5": {"new_price": 2500, "segment": "중형", "dep_rate": 0.83, "years": range(2016, 2026)},
        "K8": {"new_price": 3600, "segment": "준대형", "dep_rate": 0.84, "years": range(2021, 2026)},
        "스포티지": {"new_price": 2700, "segment": "SUV", "dep_rate": 0.85, "years": range(2016, 2026)},
        "쏘렌토": {"new_price": 3400, "segment": "SUV", "dep_rate": 0.85, "years": range(2016, 2026)},
        "EV6": {"new_price": 5300, "segment": "전기 SUV", "dep_rate": 0.80, "years": range(2021, 2026)},
    },
    "제네시스": {
        "G80": {"new_price": 6200, "segment": "준대형", "dep_rate": 0.83, "years": range(2017, 2026)},
        "GV70": {"new_price": 5700, "segment": "SUV", "dep_rate": 0.84, "years": range(2020, 2026)},
        "GV60": {"new_price": 6000, "segment": "전기 SUV", "dep_rate": 0.80, "years": range(2021, 2026)},
    },
    "쉐보레": {
        "트레일블레이저": {"new_price": 2300, "segment": "SUV", "dep_rate": 0.84, "years": range(2020, 2026)},
        "말리부": {"new_price": 2600, "segment": "중형", "dep_rate": 0.81, "years": range(2016, 2023)},
    },
    "KG모빌리티": {
        "토레스": {"new_price": 2700, "segment": "SUV", "dep_rate": 0.85, "years": range(2022, 2026)},
    },
    "르노코리아": {
        "SM6": {"new_price": 2400, "segment": "중형", "dep_rate": 0.80, "years": range(2016, 2023)},
        "QM6": {"new_price": 2600, "segment": "SUV", "dep_rate": 0.83, "years": range(2016, 2026)},
    },
    "BMW": {
        "3시리즈": {"new_price": 5500, "segment": "세단", "dep_rate": 0.83, "years": range(2016, 2026)},
        "5시리즈": {"new_price": 7200, "segment": "세단", "dep_rate": 0.83, "years": range(2016, 2026)},
        "X3": {"new_price": 6800, "segment": "SUV", "dep_rate": 0.84, "years": range(2016, 2026)},
    },
    "벤츠": {
        "C클래스": {"new_price": 5800, "segment": "세단", "dep_rate": 0.83, "years": range(2016, 2026)},
        "E클래스": {"new_price": 7500, "segment": "세단", "dep_rate": 0.83, "years": range(2016, 2026)},
        "GLC": {"new_price": 7000, "segment": "SUV", "dep_rate": 0.84, "years": range(2016, 2026)},
    },
    "아우디": {
        "A4": {"new_price": 5400, "segment": "세단", "dep_rate": 0.82, "years": range(2016, 2026)},
        "Q5": {"new_price": 6500, "segment": "SUV", "dep_rate": 0.83, "years": range(2016, 2026)},
    },
    "폭스바겐": {
        "티구안": {"new_price": 4700, "segment": "SUV", "dep_rate": 0.82, "years": range(2016, 2026)},
    },
    "토요타": {
        "캠리": {"new_price": 4200, "segment": "세단", "dep_rate": 0.85, "years": range(2016, 2026)},
        "RAV4": {"new_price": 4400, "segment": "SUV", "dep_rate": 0.86, "years": range(2019, 2026)},
    },
    "렉서스": {
        "ES": {"new_price": 6100, "segment": "세단", "dep_rate": 0.85, "years": range(2016, 2026)},
    },
    "볼보": {
        "XC60": {"new_price": 6600, "segment": "SUV", "dep_rate": 0.82, "years": range(2018, 2026)},
    },
    "미니": {
        "쿠퍼": {"new_price": 4000, "segment": "소형", "dep_rate": 0.81, "years": range(2016, 2026)},
    },
}

USED_PRICE_FLOOR_RATIO = 0.15  # 신차가 대비 최저 잔존가치 비율


def get_used_price(brand: str, model: str, year: int) -> int:
    """브랜드/모델/연식에 따른 중고차(보상판매) 가격을 만원 단위로 반환."""
    info = USED_CAR_DB[brand][model]
    age = max(CURRENT_YEAR - year, 0)
    raw = info["new_price"] * (info["dep_rate"] ** age)
    floor = info["new_price"] * USED_PRICE_FLOOR_RATIO
    price = max(raw, floor)
    return int(round(price / 10) * 10)  # 10만원 단위 반올림


# ---------------------------------------------------------------------------
# 2) 취향 질문 정의
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "key": "q1",
        "title": "차량을 고를 때 무엇을 가장 중요하게 생각하나요?",
        "options": [
            "새로운 경험 중시",
            "외관 및 디자인 중시",
            "실용적이고 합리적으로 꼼꼼하게 비교",
            "주행성능과 운전의 재미 중시",
        ],
    },
    {
        "key": "q2",
        "title": "평소 차량을 가장 많이 이용하는 순간은?",
        "options": [
            "출퇴근 등 매일 운행",
            "주말 가족과 함께 운행",
            "주말마다 여행이나 레저용으로 운행",
            "장거리 이동 시 운행",
        ],
    },
    {
        "key": "q3",
        "title": "차량을 운행하는 상황을 골라주세요",
        "options": [
            "가족과 여유롭게 여행",
            "주말마다 새로운 곳으로 이동",
            "운전을 즐기며 여유있을 때마다 이동",
            "일상에서 편하게 이동할 때 이용",
        ],
    },
]


# ---------------------------------------------------------------------------
# 3) 추천 신차 프로필 (취향 스코어 기반)
#    scores.q1/q2/q3 = 각 질문의 4개 선택지에 대한 가중치(0~3)
# ---------------------------------------------------------------------------

NEW_CAR_RECS = [
    {
        "id": "ioniq5",
        "brand": "현대",
        "model": "아이오닉5",
        "segment": "전기 SUV",
        "price": 5300,
        "tagline": "전기차의 새로운 경험, 어디든 조용하고 스마트하게",
        "desc": "미래지향적 디자인과 넉넉한 실내공간을 갖춘 순수 전기 SUV. 새로운 이동 경험을 찾는 분께 추천합니다.",
        "colors": [
            {"id": "ecotronic_gray", "name": "에코트로닉 그레이펄", "hex": "#6b6f63"},
            {"id": "abyss_black", "name": "어비스 블랙펄", "hex": "#1a1a1a"},
            {"id": "digital_green", "name": "디지털그린펄", "hex": "#2f4a44"},
            {"id": "lucid_blue", "name": "루시드블루펄", "hex": "#1f3a5c"},
            {"id": "cyber_gray", "name": "사이버 그레이 메탈릭", "hex": "#6e7178"},
            {"id": "atlas_white", "name": "아틀라스 화이트", "hex": "#f2f2f2"},
            {"id": "gravity_gold", "name": "그래비티 골드매트", "hex": "#8a7550"},
            {"id": "celadon_gray", "name": "셀라돈 그레이매트", "hex": "#9aa08f"},
            {"id": "frosted_brown", "name": "프로스티드 브라운 매트", "hex": "#a08b74"},
        ],
        "scores": {"q1": [3, 1, 0, 1], "q2": [0, 1, 3, 1], "q3": [1, 3, 1, 1]},
    },
    {
        "id": "ev6",
        "brand": "기아",
        "model": "EV6 GT-Line",
        "segment": "전기 SUV",
        "price": 5600,
        "tagline": "미래지향적 디자인과 강렬한 존재감",
        "desc": "역동적인 디자인과 개성있는 스타일을 원하는 분을 위한 고성능 전기 SUV.",
        "colors": [
            {"id": "snow_white", "name": "스노우 화이트펄", "hex": "#f5f5f5"},
            {"id": "moonscape_gray", "name": "문스케이프 매트 그레이", "hex": "#8f8a7d"},
            {"id": "ivory_silver", "name": "아이보리 매트 실버", "hex": "#d8d3c5"},
            {"id": "yacht_blue", "name": "요트 블루", "hex": "#1f4a5c"},
            {"id": "runway_red", "name": "런웨이 레드", "hex": "#8a2230"},
            {"id": "interstellar_gray", "name": "인터스텔라 그레이", "hex": "#54565a"},
            {"id": "aurora_black", "name": "오로라 블랙펄", "hex": "#131313"},
        ],
        "scores": {"q1": [2, 3, 0, 1], "q2": [0, 1, 3, 1], "q3": [1, 3, 1, 1]},
    },
    {
        "id": "gv70",
        "brand": "제네시스",
        "model": "GV70",
        "segment": "프리미엄 SUV",
        "price": 5900,
        "tagline": "품격있는 디자인과 다이나믹한 주행감성",
        "desc": "제네시스 특유의 디자인 헤리티지와 탄탄한 주행성능을 함께 갖춘 프리미엄 SUV.",
        "colors": [
            {"id": "uyuni_white", "name": "우유니 화이트", "hex": "#e9e9e6"},
            {"id": "makalu_gray", "name": "마칼루 그레이", "hex": "#5a5c5f"},
            {"id": "bering_blue", "name": "베링 블루", "hex": "#2a4a5c"},
            {"id": "seris_blue", "name": "세리스 블루", "hex": "#1f3350"},
        ],
        "scores": {"q1": [1, 3, 1, 2], "q2": [1, 2, 1, 2], "q3": [2, 2, 2, 1]},
    },
    {
        "id": "santafe",
        "brand": "현대",
        "model": "싼타페 하이브리드",
        "segment": "SUV",
        "price": 3900,
        "tagline": "넉넉한 공간과 합리적인 유지비, 가족을 위한 선택",
        "desc": "3열까지 여유로운 공간과 뛰어난 연비를 갖춘 패밀리 SUV.",
        "colors": [
            {"id": "cyber_sage", "name": "사이버 세이지 펄", "hex": "#8a9483"},
            {"id": "ecotronic_gray", "name": "에코트로닉 그레이펄", "hex": "#6b6f63"},
            {"id": "abyss_black", "name": "어비스 블랙펄", "hex": "#1c1c1c"},
            {"id": "creamy_white", "name": "크리미 화이트 펄", "hex": "#f0e9dc"},
            {"id": "earthbreath_metallic", "name": "얼씨브레스 메탈릭", "hex": "#8a7360"},
        ],
        "scores": {"q1": [0, 1, 3, 1], "q2": [1, 3, 1, 2], "q3": [3, 1, 0, 2]},
    },
    {
        "id": "sorento",
        "brand": "기아",
        "model": "쏘렌토 하이브리드",
        "segment": "SUV",
        "price": 3800,
        "tagline": "장거리도 든든하게, 실속있는 하이브리드 SUV",
        "desc": "우수한 연비와 안정적인 주행감으로 장거리 이동에 최적화된 SUV.",
        "colors": [
            {"id": "snow_white", "name": "스노우 화이트펄", "hex": "#f6f6f6"},
            {"id": "volcanic_sand_brown", "name": "볼캐닉 샌드 브라운", "hex": "#8a6a4a"},
            {"id": "cityscape_green", "name": "시티스케이프 그린", "hex": "#3f4a3f"},
            {"id": "interstellar_gray", "name": "인터스텔라 그레이", "hex": "#54565a"},
            {"id": "aurora_black", "name": "오로라 블랙 펄", "hex": "#17181a"},
        ],
        "scores": {"q1": [0, 1, 3, 1], "q2": [0, 1, 1, 3], "q3": [3, 1, 0, 2]},
    },
    {
        "id": "avante",
        "brand": "현대",
        "model": "아반떼",
        "segment": "준중형",
        "price": 2000,
        "tagline": "합리적인 가격, 매일의 출퇴근을 가볍게",
        "desc": "부담없는 가격과 우수한 연비로 매일 타기 좋은 준중형 세단.",
        "colors": [
            {"id": "volcanic_red", "name": "볼케닉 레드 펄", "hex": "#7a2a1e"},
            {"id": "abyss_black", "name": "어비스 블랙 펄", "hex": "#1a1a1a"},
            {"id": "ecotronic_gray", "name": "에코트로닉 그레이펄", "hex": "#6b6f63"},
            {"id": "serenity_copper", "name": "고요카퍼펄", "hex": "#9c6b4a"},
            {"id": "quantum_silver", "name": "퀀텀 실버 펄", "hex": "#c2c4c6"},
            {"id": "graphene_green", "name": "그라펜 그린 펄", "hex": "#3a4a3f"},
            {"id": "atlas_white", "name": "아틀라스 화이트", "hex": "#f2f2f2"},
            {"id": "kodiak_blue", "name": "코디악 블루 매트", "hex": "#3a4f5c"},
            {"id": "raptor_gray", "name": "랩터 그레이 매트", "hex": "#55585a"},
        ],
        "scores": {"q1": [0, 0, 3, 0], "q2": [3, 1, 0, 0], "q3": [0, 0, 0, 3]},
    },
    {
        "id": "k5gt",
        "brand": "기아",
        "model": "K5 GT",
        "segment": "중형",
        "price": 3100,
        "tagline": "세단의 실용성과 스포츠카의 심장",
        "desc": "고성능 터보 엔진과 스포티한 디자인으로 운전의 재미를 더한 중형 세단.",
        "colors": [
            {"id": "snow_white", "name": "스노우 화이트펄", "hex": "#eeeeee"},
            {"id": "wolf_gray", "name": "울프 그레이", "hex": "#6e6f70"},
            {"id": "interstellar_gray", "name": "인터스텔라 그레이", "hex": "#54565a"},
            {"id": "aurora_black", "name": "오로라 블랙펄", "hex": "#141414"},
        ],
        "scores": {"q1": [1, 1, 0, 3], "q2": [3, 0, 0, 1], "q3": [0, 1, 3, 1]},
    },
    {
        "id": "bmw3",
        "brand": "BMW",
        "model": "3시리즈",
        "segment": "세단",
        "price": 5700,
        "tagline": "정통 스포츠 세단의 완성, 운전의 즐거움",
        "desc": "정교한 핸들링과 강력한 주행성능으로 운전 그 자체를 즐기는 분께 추천합니다.",
        "colors": [
            {"id": "skyscraper_gray", "name": "스카이스크래퍼 그레이 메탈릭", "hex": "#4d4f52"},
            {"id": "arctic_race_blue", "name": "아틱 레이스 블루 메탈릭", "hex": "#1f4160"},
            {"id": "black_sapphire", "name": "블랙 사파이어 메탈릭", "hex": "#0f0f10"},
            {"id": "alpine_white", "name": "알파인 화이트", "hex": "#f1f1f1"},
        ],
        "scores": {"q1": [1, 1, 0, 3], "q2": [1, 0, 1, 2], "q3": [1, 1, 3, 0]},
    },
    {
        "id": "g80",
        "brand": "제네시스",
        "model": "G80",
        "segment": "준대형",
        "price": 6300,
        "tagline": "여유와 품격을 담은 플래그십 세단",
        "desc": "고급스러운 승차감과 세련된 디자인을 겸비한 대형 세단.",
        "colors": [
            {"id": "vatna_gray", "name": "바트나 그레이", "hex": "#6a6d6f"},
            {"id": "uyuni_white", "name": "우유니 화이트", "hex": "#e9e9e6"},
            {"id": "seville_silver", "name": "세빌실버", "hex": "#b8babc"},
            {"id": "makalu_gray", "name": "마칼루 그레이", "hex": "#5a5c5f"},
            {"id": "vik_black", "name": "비크 블랙", "hex": "#17181a"},
            {"id": "tasman_blue", "name": "태즈먼 블루", "hex": "#2f5a6e"},
            {"id": "ceres_blue", "name": "세레스 블루", "hex": "#22344f"},
        ],
        "scores": {"q1": [1, 3, 1, 1], "q2": [1, 3, 0, 1], "q3": [3, 1, 1, 0]},
    },
    {
        "id": "casper_ev",
        "brand": "현대",
        "model": "캐스퍼 일렉트릭",
        "segment": "소형 전기차",
        "price": 2450,
        "tagline": "도심형 라이프스타일에 꼭 맞는 실속 전기차",
        "desc": "작지만 알찬 크기와 전기차의 경제성으로 매일 부담없이 타기 좋은 도심형 모델.",
        "colors": [
            {"id": "unbleached_ivory", "name": "언블리치드 아이보리", "hex": "#e8dfc8"},
            {"id": "abyss_black", "name": "어비스 블랙펄", "hex": "#1a1a1a"},
            {"id": "atlas_white", "name": "아틀라스 화이트", "hex": "#f2f2f2"},
            {"id": "tomboy_khaki", "name": "톰보이 카키", "hex": "#6b6a4f"},
        ],
        "scores": {"q1": [1, 0, 3, 0], "q2": [3, 1, 0, 0], "q3": [0, 0, 0, 3]},
    },
]


# ---------------------------------------------------------------------------
# 3-1) 트림(등급) 옵션 - 색상 외 추가 선택 옵션
# ---------------------------------------------------------------------------

TRIM_LEVELS = [
    {"id": "standard", "name": "스탠다드", "price_delta": 0,
     "desc": "기본 안전·편의 사양 (스마트 크루즈, 후방카메라, 공조 자동화)"},
    {"id": "premium", "name": "프리미엄", "price_delta": 180,
     "desc": "스탠다드 + 통풍시트, 헤드업 디스플레이, 프리미엄 오디오"},
    {"id": "top", "name": "최상위", "price_delta": 340,
     "desc": "프리미엄 + 대형 휠, 서라운드 뷰 모니터, 첨단 주행보조 풀패키지"},
]

WHEEL_OPTIONS = [
    {"id": "18in", "name": "18인치 알로이 휠", "price_delta": 0},
    {"id": "19in", "name": "19인치 스포츠 휠", "price_delta": 40},
    {"id": "20in", "name": "20인치 대형 휠", "price_delta": 70},
]


def get_trim(trim_id: str):
    for t in TRIM_LEVELS:
        if t["id"] == trim_id:
            return t
    return TRIM_LEVELS[0]


def get_wheel(wheel_id: str):
    for w in WHEEL_OPTIONS:
        if w["id"] == wheel_id:
            return w
    return WHEEL_OPTIONS[0]


def recommend_cars(q1_idx: int, q2_idx: int, q3_idx: int, top_n: int = 3):
    """취향 응답(각 질문의 선택 인덱스 0~3)에 따라 점수순으로 추천 차량 리스트 반환."""
    scored = []
    for car in NEW_CAR_RECS:
        s = car["scores"]
        score = s["q1"][q1_idx] + s["q2"][q2_idx] + s["q3"][q3_idx]
        scored.append((score, car))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [car for _, car in scored[:top_n]]


def get_car_by_id(car_id: str):
    for car in NEW_CAR_RECS:
        if car["id"] == car_id:
            return car
    return None


# ---------------------------------------------------------------------------
# 4) 금융조건 정의 및 월 납부금 계산 (데모용 단순 산식)
# ---------------------------------------------------------------------------

FINANCE_OPTIONS = [
    {
        "id": "installment",
        "name": "할부",
        "summary": "내 소유의 차량으로, 주행거리 제한 없이 자유롭게",
        "desc": "차량을 직접 소유하며 운전 경력이 오래된 분, 주행거리 제한 없이 운행하고 싶은 분께 적합합니다.",
        "icon": "🚗",
    },
    {
        "id": "lease",
        "name": "리스",
        "summary": "부담없이 운행하고 4~5년마다 새 차로 교체",
        "desc": "차량을 유연하게 교체하며 타고 싶은 분, 평균 교체주기가 4~5년인 분께 적합합니다.",
        "icon": "🔄",
    },
    {
        "id": "rent",
        "name": "렌트",
        "summary": "신용영향 없이, 초기비용 없이 부담없이 시작",
        "desc": "신용점수에 영향 없이, 초기 비용 부담 없이 차량을 운행하고 싶은 분께 적합합니다.",
        "icon": "🛡️",
    },
]

DEFAULT_TERM_MONTHS = 48


def calc_installment(principal_10k: float, months: int = DEFAULT_TERM_MONTHS, annual_rate: float = 0.069) -> float:
    """할부 월 납부금(만원). 원리금균등상환 방식."""
    principal = max(principal_10k, 0)
    if principal == 0:
        return 0.0
    r = annual_rate / 12
    if r == 0:
        return principal / months
    payment = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return payment


def calc_lease(price_10k: float, months: int = DEFAULT_TERM_MONTHS, residual_rate: float = 0.50,
                annual_rate: float = 0.06) -> float:
    """리스 월 납부금(만원). 잔존가치 기반 단순 산식."""
    residual = price_10k * residual_rate
    depreciation = (price_10k - residual) / months
    finance_charge = (price_10k + residual) * (annual_rate / 12) / 2
    return depreciation + finance_charge


def calc_rent(price_10k: float, months: int = DEFAULT_TERM_MONTHS, residual_rate: float = 0.45,
              annual_rate: float = 0.065, service_fee_rate: float = 0.08) -> float:
    """렌트 월 납부금(만원). 리스 산식에 정비/보험 등 서비스 비용을 가산."""
    base = calc_lease(price_10k, months, residual_rate, annual_rate)
    return base * (1 + service_fee_rate)


def calc_monthly_payment(finance_id: str, principal_10k: float, full_price_10k: float,
                          months: int = DEFAULT_TERM_MONTHS) -> float:
    if finance_id == "installment":
        return calc_installment(principal_10k, months)
    elif finance_id == "lease":
        return calc_lease(full_price_10k, months)
    elif finance_id == "rent":
        return calc_rent(full_price_10k, months)
    return 0.0


def fmt_10k(value_10k: float) -> str:
    """만원 단위 숫자를 '3,800만원' 형태 문자열로 변환."""
    v = int(round(value_10k))
    return f"{v:,}만원"
