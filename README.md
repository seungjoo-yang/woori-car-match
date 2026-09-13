# 나에게 맞는 차량 찾기 (우리금융캐피탈 체험형 데모)

아이패드/터치형 노트북/휴대폰에서 관람객이 직접 조작하는 차량 추천 체험 페이지입니다.
1) 보유 차량 선택 → 2) 취향 질문 3가지 → 3) 금융조건(할부/리스/렌트) 선택 → 4) 추천 차량 및 예상 월 납부금 → 5) 색상 옵션 선택 및 이미지 확인 순서로 진행됩니다.

> 모든 차량 가격·중고차 시세·금리·월 납부금은 체험용으로 임의 산정한 값입니다. 실제 상담 시 정확한 조건을 안내해야 합니다.

## 폴더 구조

```
woori-car-match/
├── app.py                # 메인 Streamlit 앱 (화면/흐름)
├── data.py                # 중고차 시세 DB, 추천 신차 DB, 금융조건 계산 로직
├── requirements.txt
├── .streamlit/config.toml # 테마 설정
└── assets/cars/<차량id>/<색상id>.jpg  # 실제 차량 이미지 (선택, 없으면 자동 placeholder 표시)
```

## 로컬 실행 (내 컴퓨터 / 휴대폰 테스트)

```bash
cd woori-car-match
pip install -r requirements.txt
streamlit run app.py
```

같은 Wi-Fi에 연결된 휴대폰·태블릿·노트북에서 `http://<PC의 사설 IP>:8501` 로 접속하면 반응형 화면을 바로 확인할 수 있습니다. PC의 사설 IP는 터미널에 함께 출력되는 "Network URL"을 그대로 사용하면 됩니다.

> **Windows에서 `streamlit run app.py`가 `ModuleNotFoundError: No module named 'streamlit.cli'` 오류를 낼 경우**: PATH에 잡혀있는 `streamlit` 명령이 (Anaconda 등) 다른 파이썬 환경의 오래된 실행 파일을 가리키고 있는 경우입니다. 이때는 `streamlit` 대신 아래처럼 실행하세요.
> ```bash
> python -m streamlit run app.py
> ```

## 실제 차량 이미지 넣는 방법

`data.py`의 `NEW_CAR_RECS`에 정의된 차량 `id`와 색상 `id`를 그대로 폴더/파일명으로 사용하면, 코드 수정 없이 자동으로 실제 이미지가 우선 표시됩니다. (이미지가 없으면 색상이 반영된 자리표시 이미지가 대신 표시됩니다.)

```
assets/cars/ioniq5/black.jpg
assets/cars/ioniq5/white.jpg
assets/cars/ev6/green.jpg
...
```

차량 id / 색상 id 목록은 `data.py`의 `NEW_CAR_RECS`를 확인하세요.

## 데이터 커스터마이징

- `USED_CAR_DB` : 보유 차량(중고차) 브랜드/모델/연식별 시세 — 신차가 기준 감가율로 자동 계산됩니다.
- `NEW_CAR_RECS` : 추천 신차 목록. 각 차량마다 3가지 질문(4개 선택지)에 대한 가중치(`scores`)가 있어, 응답 조합에 따라 점수가 가장 높은 차량이 추천됩니다.
- `FINANCE_OPTIONS`, `calc_installment / calc_lease / calc_rent` : 할부·리스·렌트 월 납부금 계산 산식(데모용 단순화 버전).

## Streamlit Community Cloud 배포

1. 이 `woori-car-match` 폴더를 GitHub 저장소로 푸시합니다 (public 또는 private 모두 가능).
2. https://share.streamlit.io 접속 → GitHub 계정 연결 → "New app".
3. 저장소/브랜치 선택, Main file path에 `app.py` 지정 후 배포.
4. 배포가 끝나면 발급된 URL을 아이패드/노트북 브라우저에서 열면 됩니다 (전시 부스에서는 URL을 브라우저 즐겨찾기 또는 QR코드로 고정해두면 편리합니다).

## 전시용 팁

- 태블릿/노트북에서는 브라우저 "전체화면(F11)" 또는 키오스크 모드로 열어두면 주소창 없이 깔끔하게 체험할 수 있습니다.
- 관람객마다 새로 시작할 수 있도록, 마지막 화면의 "처음부터 다시 하기" 버튼을 안내해 주세요.
