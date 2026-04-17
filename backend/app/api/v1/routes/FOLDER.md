# FOLDER.md

> **파일명**: FOLDER.md
> **폴더 경로**: `backend/app/api/v1/routes/`
> **최종 수정일**: 2026-04-18
> **문서 해시**: SHA256:TBD
> **문서 역할**: API v1 라우트 핸들러 폴더 명세
> **문서 우선순위**: reference
> **연관 문서**: API_SPEC.md, DIRECTORY_SPEC.md, backend/app/api/v1/router.py

---

## 1. 용도

FastAPI 라우트 핸들러를 모듈별로 둔다. 각 파일은 `APIRouter`를 노출하며 `router.py`에서 집결한다.

---

## 2. 파일 목록

| 파일 | 엔드포인트 | 상태 |
|---|---|---|
| `recommendation.py` | `POST /api/v1/recommendations`, `POST /api/v1/recommendations/evidence` | ✅ |
| `roadmap.py` | `POST /api/v1/roadmaps` | ✅ |
| `risk.py` | `GET /api/v1/risk-stages` | ✅ |
| `health.py` | `GET /api/v1/health` | ✅ |
| `schedule.py` | 시험 일정 관련 (reserved) | 🔄 reserved |
| `admin.py` | 내부 관리용 (캐시 flush 등) | ✅ |

---

## 3. 담지 않는 것

- 비즈니스 로직 → `backend/app/services/`
- 데이터 스키마 정의 → `backend/app/schemas/`
- DB 접근 → `backend/app/repositories/`

## 4. 연계

`routes/` → `services/` → `data/canonical/` (candidates / relations)
