# Rare Source (희귀 부품 메타 검색 플랫폼) 🚀

이 프로젝트는 산업용 장비의 유지보수를 위한 희귀/단종 부품(EOL)을 전 세계 브로커 네트워크에서 발굴하는 메타 검색 플랫폼입니다.

## 📂 프로젝트 구조
- backend/: FastAPI 기반의 검색 엔진 (Verical, Win Source, Meta Aggregator 통합)
- frontend/: React + Vite 기반의 프리미엄 UI (Treasure Hunter UX 적용)

## 🛠 실행 방법

### 1. 백엔드 서버 실행
```bash
cd backend
python3 main.py
```
*서버가 http://localhost:8000 에서 실행됩니다.*

### 2. 프론트엔드 실행
```bash
cd frontend
npm install
npm run dev
```
*브라우저에서 http://localhost:5173 에 접속하세요.*

## ✨ 주요 기능
- Global Scout: 전 세계 브로커 네트워크 실시간 스캔 애니메이션.
- Risk Assessment: 부품별 리스크 레벨(Low/Medium/High) 시각화.
- QC Add-on: 신뢰할 수 없는 재고에 대한 정밀 검수 옵션 추가.
- Secure Transaction: 백투백 매입 주문 시뮬레이션.
