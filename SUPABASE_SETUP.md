# Supabase 설정 가이드

RareSource 캐싱 시스템을 활성화하려면 Supabase 프로젝트를 생성하고 설정해야
합니다.

## 1. Supabase 프로젝트 생성

1. https://supabase.com 접속 및 회원가입
2. "New Project" 클릭
3. 프로젝트 이름: `raresource-cache`
4. Database Password 설정 (안전하게 보관!)
5. Region 선택: `Northeast Asia (Seoul)` 추천
6. 프로젝트 생성 (2-3분 소요)

## 2. 캐시 테이블 생성

### SQL Editor에서 실행

1. 왼쪽 메뉴에서 "SQL Editor" 클릭
2. "New query" 클릭
3. `backend/search_cache_schema.sql` 파일 내용 복사&붙여넣기
4. "Run" 버튼 클릭

테이블이 생성되면 "Table Editor"에서 `search_cache` 테이블을 확인할 수 있습니다.

## 3. API 키 발급

### Project Settings에서

1. 왼쪽 메뉴 하단 "Settings" 클릭
2. "API" 섹션 선택
3. 다음 정보 복사:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon/public key**: `eyJhb...` (매우 긴 문자열)

## 4. 환경 변수 설정

`.env` 파일에 추가:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

## 5. 백엔드 재시작

```bash
# 터미널에서 Ctrl+C로 기존 서버 중지
cd backend
python3 main.py
```

## 6. 테스트

### 최초 검색 (캐시 미스)

```
검색: LM358
✗ Cache MISS for LM358
🔍 Scraping FindChips...
✓ Cached 5 results for LM358 (expires in 1h)
```

### 재검색 (캐시 히트)

```
검색: LM358
✓ Cache HIT for LM358 (age: 5s)
```

---

## 옵션: Row Level Security (보안 강화)

Supabase의 RLS를 활성화하여 보안 강화 가능:

```sql
ALTER TABLE search_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow anonymous read access" 
ON search_cache FOR SELECT 
TO anon 
USING (true);

CREATE POLICY "Allow service role full access"
ON search_cache FOR ALL
TO service_role
USING (true);
```

---

## 문제 해결

### "Supabase credentials missing"

- `.env` 파일에 `SUPABASE_URL`과 `SUPABASE_KEY`가 있는지 확인
- 백엔드 재시작

### "Table doesn't exist"

- SQL 스키마가 올바르게 실행되었는지 확인
- Supabase Table Editor에서 `search_cache` 테이블 존재 확인

### 캐시가 작동하지 않음

- 터미널 로그에서 "Cache HIT/MISS" 메시지 확인
- Supabase 프로젝트가 활성 상태인지 확인
