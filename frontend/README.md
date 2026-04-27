# frontend/README.md

> **파일명**: frontend/README.md  
> **최종 수정일**: 2026-04-27  
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

---

## UX 병목 현황 (2026-04-27 기준)

### 완료
- [x] `location.state` 새로고침 소실 → URL search params(`?stage=`, `?cert=`)으로 대체
- [x] StepIndicator 완료 판정 오류 → params 존재 여부 기준으로 수정
- [x] 라우트 전환 시 스크롤·포커스 미복귀 → `useEffect` + `mainRef.focus()`
- [x] 대형 JSON 검색 버벅임 → `useDeferredValue` 적용
- [x] `useAsync` 훅 → API 연동 준비 패턴 (`src/hooks/useAsync.ts`)

### 다음 처리할 병목 (우선순위 순)
1. **로딩·에러 UI 없음** — 페이지별 로딩 스피너·에러 메시지 skeleton 필요. `useAsync`는 준비됐으나 아직 페이지에 미연결.
2. **자격증 카드 내 ID 노출** — `cert-chip`에 `cert_013` 등 내부 ID가 그대로 노출. cert_candidates.json에 이름 매핑 필요 또는 백엔드 API 응답에서 이름 포함.
3. **"설명 근거" 버튼 동작 없음** — Recommendation 카드의 `ExternalLink` 버튼이 no-op. RAG evidence 연동 전까지 비활성화 처리 필요.
4. **결과 페이지네이션 없음** — Recommendation은 최대 50건 슬라이싱만 됨. "더 보기" 버튼 또는 가상 스크롤 필요.
5. **모바일 StepIndicator 가독성** — 소형 화면(320px 이하)에서 단계 라벨이 겹침. 모바일 전용 compact 뷰 처리 필요.
6. **검색창 초기화 버튼 없음** — 검색어 입력 후 지우는 X 버튼 부재. UX 마찰.
