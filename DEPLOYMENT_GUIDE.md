# Rare Source 배포 가이드 (One-Click Launch)

이 문서는 코딩 지식 없이 GitHub, Render, Supabase를 연결하여 서비스를 출시하는
방법을 설명합니다.

## 1단계: GitHub에 코드 올리기

1. GitHub.com에 로그인하고 우측 상단 `+` -> `New repository` 클릭
2. Repository name에 `RareSource` 입력 후 `Create repository` 클릭
3. 터미널에서 아래 명령어 입력 (한 줄씩):

```bash
cd /Users/kimdoyeon/Documents/RareSource
git init
git add .
git commit -m "Initial launch"
git branch -M main
git remote add origin https://github.com/사용자아이디/RareSource.git
git push -u origin main
```

_(GitHub 주소는 방금 만든 레포지토리 페이지에서 확인 가능합니다)_

---

## 2단계: 백엔드 서버 (Render)

1. [Render.com](https://render.com) 접속 및 로그인
2. `New` -> `Web Service` 클릭
3. `Build and deploy from a Git repository` 선택
4. GitHub 연결 후 방금 만든 `RareSource` 리포지토리 선택
5. 설정 입력:
   - **Name**: `raresource-backend`
   - **Region**: `Singapore` (한국과 가까움)
   - **Root Directory**: `backend` (중요!)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
   - **Instance Type**: `Free`
6. `Create Web Service` 클릭

_몇 분 뒤 `https://raresource-backend.onrender.com` 같은 주소가 생성됩니다._

---

## 3단계: 프론트엔드 (Vercel - 추천)

Render에서도 가능하지만 Vercel이 설정이 더 쉽습니다.

1. [Vercel.com](https://vercel.com) 접속 및 로그인
2. `Add New...` -> `Project` 클릭
3. GitHub의 `RareSource` 리포지토리 Import
4. **Framework Preset**: `Vite` 선택
5. **Root Directory**: `Edit` 눌러서 `frontend` 선택 (중요!)
6. **Deploy** 클릭

---

## 4단계: Supabase (데이터베이스)

1. [Supabase.com](https://supabase.com) 접속 및 `New Project` 생성
2. Project URL과 Anon Key를 복사
3. Vercel(프론트엔드) 설정 페이지 (`Settings` -> `Environment Variables`)로 이동
4. 변수 추가:
   - `VITE_SUPABASE_URL`: (복사한 URL)
   - `VITE_SUPABASE_ANON_KEY`: (복사한 Key)
5. Vercel에서 `Redeploy` 클릭

---

## 🚀 출시 완료!

이제 Vercel이 제공한 주소(예: `raresource.vercel.app`)로 접속하면 전 세계
어디서든 이용 가능한 서비스가 됩니다!
