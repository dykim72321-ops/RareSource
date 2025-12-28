# 실제 API 연결 가이드 (무료 티어 전용)

이 가이드는 **무료 또는 저비용**으로 실제 전자부품 데이터를 연결하는 방법을
설명합니다.

---

## 📋 추천 무료 API 목록

### 1. Digi-Key API ⭐️ (최우선 추천)

- **무료 티어**: 1,000 요청/일
- **데이터 품질**: ⭐️⭐️⭐️⭐️⭐️
- **가입 난이도**: 중간 (사업자 정보 필요)
- **신청 링크**: https://developer.digikey.com/

#### 가입 절차:

1. Digi-Key Developer Portal 접속
2. `Create Account` 클릭
3. 회사 정보 입력 (개인 프로젝트는 "Individual"로 선택)
4. API Application 생성 → `Client ID`와 `Client Secret` 발급
5. OAuth 2.0 인증 설정

---

### 2. Mouser API ⭐️⭐️⭐️⭐️

- **무료 티어**: 1,000 요청/일
- **데이터 품질**: ⭐️⭐️⭐️⭐️
- **가입 난이도**: 쉬움
- **신청 링크**: https://www.mouser.com/api-hub/

#### 가입 절차:

1. Mouser 계정 생성
2. API Hub에서 Search API 신청
3. API Key 즉시 발급 (이메일로 전송)

---

### 3. Octopart API (Nexar) ⭐️⭐️⭐️

- **무료 티어**: 100 요청/일 (제한적)
- **데이터 품질**: ⭐️⭐️⭐️⭐️⭐️ (가장 많은 데이터 집계)
- **가입 난이도**: 중간
- **신청 링크**: https://nexar.com/api

---

### 4. Arrow API ⭐️⭐️⭐️

- **무료 티어**: 제한적
- **데이터 품질**: ⭐️⭐️⭐️⭐️
- **가입 난이도**: 어려움 (파트너십 필요)

---

## 🔧 우리 시스템에 적용하기

### Step 1: API 키 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하세요:

```bash
# .env (절대 GitHub에 올리지 마세요!)
DIGIKEY_CLIENT_ID=your_digikey_client_id
DIGIKEY_CLIENT_SECRET=your_digikey_client_secret
MOUSER_API_KEY=your_mouser_api_key
OCTOPART_API_KEY=your_octopart_api_key
```

### Step 2: Python에서 환경 변수 불러오기

`backend/main.py`에 다음 코드를 추가:

```python
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

DIGIKEY_CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID")
DIGIKEY_CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET")
MOUSER_API_KEY = os.getenv("MOUSER_API_KEY")
```

### Step 3: 의존성 설치

```bash
cd backend
pip install python-dotenv requests
```

---

## 🚀 실제 API 호출 예제 (Digi-Key)

제가 이미 `FreeApiConnector` 클래스를 만들어뒀습니다.\
이제 **실제 Digi-Key API**를 호출하도록 업그레이드하겠습니다.

코드는 `backend/scraper_examples.py`에서 확인 가능합니다.

---

## 💰 비용 최적화 전략

1. **캐싱**: 같은 부품을 1시간 내에 다시 검색하면 DB에서 불러오기
2. **병렬 호출**: 여러 API를 동시에 호출해서 가장 빠른 결과 사용
3. **Fallback**: API가 실패하면 웹 스크래핑으로 자동 전환

---

## ⚠️ 주의사항

- `.env` 파일은 **절대 GitHub에 올리지 마세요** (이미 `.gitignore`에 추가됨)
- 무료 티어 한도를 초과하면 요청이 차단됩니다
- 상업적 용도로 사용 시 각 API의 약관을 확인하세요

---

## 📞 다음 단계

1. 위 링크에서 **Digi-Key API 키**를 신청하세요
2. 발급받은 키를 저에게 알려주시면 바로 코드에 적용해드립니다
3. 테스트 후 다른 API(Mouser 등)도 추가로 연결합니다

**API 키를 발급받으셨나요? 아니면 제가 신청 과정을 스크린샷과 함께 더 자세히
설명해드릴까요?**
