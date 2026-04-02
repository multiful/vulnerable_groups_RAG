# frontend/README.md

> **파일명**: frontend/README.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 프론트엔드 디렉터리 안내  
> **문서 우선순위**: reference  
> **연관 문서**: DIRECTORY_SPEC.md, API_SPEC.md  
> **참조 규칙**: 폴더 트리는 `DIRECTORY_SPEC.md` §4.3과 맞춘다. 빈 디렉터리 추적용 `.gitkeep`만 두었다.

---

## 스택

React 19 + Vite 6 + TypeScript. 경로 별칭 `@/` → `src/`.

## 로컬 실행

```bash
cd frontend
npm install
npm run dev
```

- 기본 포트 `5173`
- `vite.config.ts` 에서 `/api` 를 `http://127.0.0.1:8000` 으로 **프록시**하므로, 로컬에서는 `VITE_API_BASE_URL` 없이도 `/api/v1/health` 호출 가능

## 프로덕션 (Vercel)

- `npm run build` 산출물 배포
- API가 별 도메인이면 `VITE_API_BASE_URL=https://your-api.example.com` 설정 후 빌드 (프록시 없음)
- 백엔드 `CORS_ORIGINS` 에 Vercel 도메인 추가
