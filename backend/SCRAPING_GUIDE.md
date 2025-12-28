# Web Scraping 설치 및 테스트 가이드

## 1단계: 필수 라이브러리 설치

터미널에서 백엔드 폴더로 이동 후 실행:

```bash
cd /Users/kimdoyeon/Documents/RareSource/backend

# 가상환경 활성화 (이미 했다면 Skip)
source venv/bin/activate

# 스크래핑 라이브러리 설치
pip install httpx beautifulsoup4 lxml

# (선택) 동적 사이트용 Playwright
pip install playwright
playwright install chromium
```

## 2단계: 예제 스크래퍼 테스트

제가 만든 `scraper_examples.py` 파일을 실행해 보세요:

```bash
python3 scraper_examples.py
```

정상 작동하면 다음과 같은 출력이 나옵니다:

```
🔍 웹 스크래핑 테스트 시작...
검색 중: TMS320C25
==================================================
✅ 총 2개의 결과를 찾았습니다:
1. Digi-Key - $12.50 (450 units)
2. Digi-Key Global - $15.00 (200 units)
```

## 3단계: 실제 사이트에 적용하기

### 방법 A: 간단한 HTML 사이트 스크래핑

`scraper_examples.py`의 `scrape_octopart_example()` 함수를 수정:

```python
# 실제 URL로 변경
url = f"https://목표사이트.com/search?q={mpn}"
response = await client.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Chrome DevTools로 HTML 구조 분석 후
price = soup.select_one('.가격클래스명').text
stock = soup.select_one('.재고클래스명').text
```

### 방법 B: 공식 API 사용 (가장 권장)

1. Digi-Key API 키 발급: https://developer.digikey.com/
2. Mouser API 키 발급: https://www.mouser.com/api-hub/
3. `scraper_examples.py`의 API 함수에 키 입력

### 방법 C: Playwright로 복잡한 사이트

JavaScript로 렌더링되는 사이트는 `scrape_with_playwright_example()` 사용

## 4단계: main.py에 통합

실제 스크래퍼가 완성되면 `backend/main.py`의 Mock 함수들을 교체:

```python
# 기존 Mock 함수
async def fetch_tier1_api(query: str):
    # ... Mock 데이터 ...

# 실제 스크래퍼로 교체
from scraper_examples import scrape_octopart_example

async def fetch_tier1_api(query: str):
    return await scrape_octopart_example(query)
```

## 주의사항

### ⚖️ 법적 고려사항

- **robots.txt 확인**: `https://사이트.com/robots.txt`
- **이용약관 검토**: 스크래핑이 금지되어 있는지 확인
- **공식 API 우선**: API가 있다면 반드시 API 사용

### 🛡️ 차단 방지 기술

```python
# 1. Request 간격 두기
await asyncio.sleep(1)  # 1초 대기

# 2. User-Agent 랜덤화
import random
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
]
headers = {'User-Agent': random.choice(user_agents)}

# 3. 프록시 사용 (고급)
proxies = {
    "http://": "http://프록시주소:포트",
}
```

## 다음 단계

1. 먼저 `scraper_examples.py` 테스트 실행
2. 타겟 사이트 하나를 정해서 실제 스크래퍼 작성
3. `main.py`에 통합
4. 에러 처리 및 재시도 로직 추가
