# Content Hash: SHA256:TBD
"""Generate FOLDER.md scaffold notes under leaf directories (one-off / re-runnable)."""
from __future__ import annotations

from pathlib import Path

def _repo_root() -> Path:
    p = Path(__file__).resolve().parent
    for _ in range(6):
        if (p / "DIRECTORY_SPEC.md").is_file():
            return p
        p = p.parent
    return Path(__file__).resolve().parents[2]


ROOT = _repo_root()

REF_RULES = """> **참조 규칙**: 폴더 용도가 바뀌면 본 파일과 `DIRECTORY_SPEC.md`를 같은 작업에서 갱신한다. 실제 스키마·API 계약은 루트 `DATA_SCHEMA.md`, `API_SPEC.md`, `RAG_PIPELINE.md`가 우선한다.

---
"""

FOOTER = """
---

## 4. 비고

- 비어 있거나 `.gitkeep`만 둔 것은 **개발 스캐폴드**일 수 있다.
- 대용량 원본·산출물은 Git 정책(`.gitignore`)과 `HASH_INCREMENTAL_BUILD_GUIDE.md` 증분 원칙을 따른다.
"""


def block(rel_path: str, purpose: str, avoid: str, links: str) -> str:
    return f"""# FOLDER.md

> **파일명**: FOLDER.md  
> **폴더 경로**: `{rel_path}`  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:TBD  
> **문서 역할**: 디렉터리 스캐폴드 명시서 — 담는 내용·금지·다음 단계 연계  
> **문서 우선순위**: reference (충돌 시 루트 기준 문서 우선)  
> **연관 문서**: DIRECTORY_SPEC.md, SYSTEM_ARCHITECTURE.md, RAG_PIPELINE.md, DATA_SCHEMA.md, PRD.md, PROJECT_SUMMARY.md, README.md, CHANGE_CONTROL.md  

{REF_RULES}
## 1. 용도

{purpose}

## 2. 담지 않는 것

{avoid}

## 3. 산출·연계

{links}
{FOOTER}"""


SPECS: dict[str, tuple[str, str, str]] = {
    # --- docs ---
    "docs/slides": (
        "발표·리뷰용 슬라이드 원본(PPT/PDF보내기 등)을 둔다. 제품 계약·스키마의 근거 문서는 아니다.",
        "실행 코드, secrets, 대용량 미디어(팀 정책으로 제외한 것).",
        "`ROOT_DOC_GUIDE.md`에서 문서 탐색 시 참고 자료로만 연결한다.",
    ),
    "docs/references": (
        "논문, 블로그, 장문 기법 가이드 등 **외부·일반론 레퍼런스**를 둔다. (예: Advanced RAG indexing 가이드)",
        "이 프로젝트의 단일 기준선(루트 md와 동일 내용의 복제본으로 삼지 않는다).",
        "아키텍처 **결정**은 `docs/architecture/` 및 루트 `SYSTEM_ARCHITECTURE.md`에 반영한다.",
    ),
    "docs/architecture": (
        "이 저장소 전용 구조도, 시퀀스, SQL 템플릿 등 **우리 시스템 설계 산출**을 둔다.",
        "제품 범위·기능 정의 전문(그건 `PRD.md`, `FEATURE_SPEC.md`).",
        "`RAG_PIPELINE.md` / `SYSTEM_ARCHITECTURE.md`와 상호 링크·동기화를 유지한다.",
    ),
    "docs/meeting_notes": (
        "회의록, 의사결정 메모, 액션 아이템을 둔다.",
        "canonical 데이터·청크 등 기계 처리 입력(그건 `data/`).",
        "확정된 결정은 해당 루트 문서로 옮기고 여기엔 맥락만 남긴다.",
    ),
    # --- data raw ---
    "data/raw/pdf": (
        "born-digital·스캔 혼합 등 **원본 PDF**. Parse 및 이후 RAG 인덱싱 입력의 출발점이다.",
        "CSV, Parse IR JSON(그건 각각 `data/raw/csv/`, `data/index_ready/parse_ir/`).",
        "`RAG_PIPELINE.md` Parse 단계 → `data/index_ready/` 산출로 이어진다.",
    ),
    "data/raw/html": (
        "수집한 **원본 HTML** (공지·안내 페이지 저장본 등). 텍스트 추출·청킹의 입력이다.",
        "정규화된 청크·벡터(그건 `data/index_ready/`).",
        "Parse 규칙·증분 키는 `RAG_PIPELINE.md`, `HASH_INCREMENTAL_BUILD_GUIDE.md`를 따른다.",
    ),
    "data/raw/csv": (
        "마스터·매핑 등 **구조화 원본 CSV**. canonicalization의 입력이다. **Parse IR을 만들지 않는다.**",
        "PDF/HTML 원본, 임의 더미 row(정책 위반).",
        "`CSV_CANONICALIZATION_TEAM_GUIDE.md` → `data/canonical/` 산출.",
    ),
    "data/raw/api": (
        "후속 스프린트용 **API 스냅샷·수집 결과**를 둘 자리다. 현재는 `PRD.md` 기준 **reserved**.",
        "운영 secret, 인증 토큰이 포함된 평문 저장.",
        "스키마 확정 시 `DATA_SCHEMA.md` 및 canonical 경로와 합류한다.",
    ),
    # --- taxonomy ---
    "data/taxonomy": (
        "허용 **도메인·직무·위험군 마스터** (`domain_v2.txt`, `prefer_job.txt`, `risk_stage_master.csv` 등). `related_domains` / `related_jobs` 검증의 기준선.",
        "자유 텍스트 taxonomy, 추천 후보 row(그건 `data/canonical/candidates/`).",
        "`DATA_SCHEMA.md` taxonomy 규칙과 반드시 정합을 맞춘다.",
    ),
    # --- canonical ---
    "data/canonical/entities": (
        "CSV 파이프라인에서 생성한 **정규화 엔티티** 행·파일을 둔다.",
        "문서형 chunk, PDF Parse IR.",
        "`DATA_SCHEMA.md` 엔티티 정의 및 `build_entities` 스크립트와 연계.",
    ),
    "data/canonical/relations": (
        "엔티티 간 **관계** 산출물을 둔다.",
        "원본 CSV 직접 복사본(원본은 `data/raw/csv/`).",
        "`build_relations` → 추천 그래프·후보 생성 입력.",
    ),
    "data/canonical/candidates": (
        "**추천 candidate row** 등 구조적 추천 입력을 둔다. RAG chunk와 동일 구조로 취급하지 않는다.",
        "벡터 임베딩 파일, 긴 설명 텍스트 단독 저장소.",
        "`FEATURE_SPEC.md`·`DATA_SCHEMA.md`의 candidate 계약을 따른다.",
    ),
    "data/canonical/validation": (
        "스키마 검증 리포트, 불일치 목록, 수동 큐레이션 로그 등 **품질 게이트 산출**.",
        "원본 전체 백업(용량·민감정보 분리 정책 따름).",
        "CI 또는 `scripts/maintenance`에서 갱신 가능.",
    ),
    # --- index_ready ---
    "data/index_ready/parse_ir": (
        "PDF/HTML Parse **중간 표현(IR)**. 청킹 전 단계 산출물.",
        "CSV canonical 결과, 최종 임베딩.",
        "`chunk_version` / `parse_hash` 등은 `HASH_INCREMENTAL_BUILD_GUIDE.md` 참고.",
    ),
    "data/index_ready/chunks": (
        "RAG용 **청크 JSONL** 등(예: `chunks.jsonl`). 검색 단위 텍스트와 메타.",
        "추천 candidate row(구조 레인).",
        "`RAG_PIPELINE.md` §7·§8, `backend/rag/ingest/chunk_loader.py` 스키마에 맞춘다.",
    ),
    "data/index_ready/metadata": (
        "청크·문서 단위 **부가 메타데이터** 파일(필터·출처 표시용)을 둔다.",
        "단일 거대 JSON에 모든 것을 몰아넣기(운영 시 분리·증분 어려움).",
        "임베딩 입력 조립 시 `metadata_version` 갱신 정책을 따른다.",
    ),
    "data/index_ready/dense_input": (
        "Dense 임베딩 API/배치에 넘기기 직전 **정규화된 텍스트 스냅** 등을 둘 수 있다.",
        "원본 PDF, secret.",
        "`embedding_version` 변경 시 선택적 재처리 — `RAG_PIPELINE.md` §9.",
    ),
    "data/index_ready/sparse_input": (
        "BM25·sparse용 `text_for_sparse` 등 **역색인 입력**을 둘 자리. **exact miss가 재현될 때만** 활성화(`RAG_PIPELINE.md`).",
        "기본 파이프라인에서 필수 산출로 강제하지 않는다.",
        "Hybrid 도입 시 스토어 스키마와 조인 키(`chunk_id`)를 맞춘다.",
    ),
    # --- processed ---
    "data/processed/merged": (
        "여러 소스 병합 **중간 테이블·스냅**을 둔다.",
        "원본 단일 소스의 진실 공급원(원본은 `data/raw/`).",
        "병합 규칙은 `DATA_SCHEMA.md`·배치 스크립트에 문서화.",
    ),
    "data/processed/snapshots": (
        "특정 시점 **데이터 스냅샷**(재현·감사용)을 둔다.",
        "일상 증분의 유일한 저장소로 쓰지 않는다(증분은 해시 기반).",
        "`EXPERIMENT_GUIDE.md` / `EVALUATION.md`와 실험 ID를 맞출 수 있다.",
    ),
    # --- experiments ---
    "experiments/configs": (
        "실험용 **하이퍼파라미터·모델명·데이터 서브셋** YAML/JSON.",
        "프로덕션 `.env`, 비밀.",
        "`EXPERIMENT_GUIDE.md` 재현 절차와 짝을 맞춘다.",
    ),
    "experiments/logs": (
        "실험 실행 **로그**, CLI 출력 캡처.",
        "대용량 trace(팀 정책에 따라 외부 스토리지).",
        "`EVALUATION.md`에 요약 지표만 남기고 원본은 여기 보관 가능.",
    ),
    "experiments/reports": (
        "비교표, 그림, **리포트 Markdown/PDF**.",
        "미검증 가설을 확정 사실처럼 루트 문서에 붙이지 않는다.",
        "결론이 제품에 반영되면 `PRD.md`·`EVALUATION.md`를 갱신.",
    ),
    "experiments/baselines": (
        "**베이스라인** 결과·체크포인트 메타를 둔다.",
        "거대 모델 가중치(별도 아티팩트 저장소 권장).",
        "`EVALUATION_GUIDELINE.md`의 baseline 정의와 맞춘다.",
    ),
    "experiments/notebooks": (
        "탐색적 분석 **Jupyter** 등. 재현은 스크립트로 승격하는 것을 권장.",
        "장기 유지 필요한 파이프라인 로직(그건 `backend/` 또는 `scripts/`).",
        "핵심 발견은 `EVALUATION.md` 또는 루트 문서에 반영.",
    ),
    # --- infra ---
    "infra/docker": (
        "컨테이너 **Dockerfile·compose 조각** 등.",
        "로컬 `.env` 실값.",
        "전체 배포는 현재 **reserved** — `DIRECTORY_SPEC.md` §4.7.",
    ),
    "infra/deploy": (
        "배포 스크립트·매니페스트 자리. 현재 스캐폴드.",
        "비밀번호·키.",
        "`infra/env/.env.example`과 변수명을 맞춘다.",
    ),
    "infra/env": (
        "**환경 변수 템플릿** (예: `.env.example`). 실제 `.env`는 Git에 올리지 않는다.",
        "비밀 값이 포함된 파일.",
        "루트 `.gitignore`의 `!.env.example` 예외 정책을 따른다.",
    ),
    # --- shared ---
    "shared/constants": (
        "프론트·백엔드가 공유하는 **상수**.",
        "도메인 비즈니스 규칙 전부(그건 문서·서버 검증).",
        "타입과 함께 `shared/types`와 동기화.",
    ),
    "shared/schemas": (
        "JSON Schema 등 **공유 스키마 초안**.",
        "단일 진실 `DATA_SCHEMA.md`와 충돌 시 문서 우선.",
        "API 페이로드는 `API_SPEC.md`와 정합.",
    ),
    "shared/types": (
        "공용 **TypeScript 타입** 등.",
        "서버 전용 Pydantic 모델(그건 `backend/`).",
        "OpenAPI 생성 시 단일 출처를 정해 드리프트를 방지.",
    ),
    # --- scripts ---
    "scripts/parse": (
        "`DIRECTORY_SPEC.md` 기준 **PDF/HTML parse** 배치 진입점. `run.py` 스텁.",
        "CSV canonicalize(그건 `scripts/canonicalize/`).",
        "산출은 `data/index_ready/parse_ir/` 등으로 — `RAG_PIPELINE.md`.",
    ),
    "scripts/canonicalize": (
        "**CSV → canonical** 변환 배치.",
        "문서 청킹.",
        "`CSV_CANONICALIZATION_TEAM_GUIDE.md`, `data/canonical/`",
    ),
    "scripts/build_entities": (
        "**entity row 생성** 배치.",
        "relation, candidate(각각 전용 스크립트).",
        "`data/canonical/entities/`",
    ),
    "scripts/build_relations": (
        "**relation row 생성** 배치.",
        "엔티티 정의 변경 없이 relation만 돌릴 때 사용.",
        "`data/canonical/relations/`",
    ),
    "scripts/build_candidates": (
        "**candidate row 생성** 배치.",
        "RAG 임베딩.",
        "`data/canonical/candidates/`",
    ),
    "scripts/evaluation": (
        "오프라인 **평가·골든셋 스크립트** 진입.",
        "프로덕션 서빙 코드.",
        "`EVALUATION_GUIDELINE.md`, `experiments/reports/`",
    ),
    "scripts/maintenance": (
        "일관성 점검, **FOLDER.md 생성기** 등 유지보수 스크립트.",
        "일회성 데이터 편집(수동은 문서화).",
        "`DEV_LOG.md`에 중요 작업 기록.",
    ),
    # --- frontend (leaves) ---
    "frontend/public/assets": (
        "빌드에 포함되는 **정적 에셋**(파비콘, 정적 이미지 등).",
        "대용량 원본 미디어 라이브러리(별도 CDN·스토리지 검토).",
        "`frontend` 빌드 산출물은 `dist/` (Git 제외).",
    ),
    "frontend/src/app": (
        "앱 셸·라우팅 래퍼 등 **앱 루트** 모듈을 둘 자리.",
        "페이지별 화면 전체(그건 `pages/`).",
        "`App.tsx`와 조율.",
    ),
    "frontend/src/pages/Home": (
        "**홈(랜딩)** 페이지 컴포넌트. 서비스 상태·헬스 확인 등 진입.",
        "도메인 비즈니스 로직 단독 캡슐(그건 `features/`).",
        "`API_SPEC.md`의 공개 API 클라이언트와 연동.",
    ),
    "frontend/src/pages/RiskAssessment": (
        "**위험군 평가** UI 자리. `PRD.md` 위험군 1~5단계 입력·표시.",
        "추천 점수 계산 서버 로직(그건 `backend/`).",
        "`FEATURE_SPEC.md` 위험군 기능.",
    ),
    "frontend/src/pages/Recommendation": (
        "**자격증 추천** 결과 화면.",
        "RAG 인덱스 빌드(그건 오프라인 파이프라인).",
        "구조적 추천 API + evidence API — `API_SPEC.md`.",
    ),
    "frontend/src/pages/Roadmap": (
        "**로드맵** 단계형 UI.",
        "일정 API 실연동(`FEATURE_SPEC` reserved).",
        "`roadmap` feature 모듈과 연계.",
    ),
    "frontend/src/pages/Schedule": (
        "**일정** 화면 자리. 현재 **reserved** — 목업만 가능.",
        "실시간 시험일정 API 연동(미구현 시 사용자 오해 유발 컨텐츠).",
        "`FEATURE_SPEC.md`, `PRD.md` 비범위 확인.",
    ),
    "frontend/src/pages/Admin": (
        "**관리** 화면 자리. **reserved**.",
        "운영 데이터 무단 노출.",
        "인증·RBAC 설계 후 활성화.",
    ),
    "frontend/src/components/layout": (
        "헤더·푸터·쉘 등 **레이아웃** 컴포넌트.",
        "페이지별 비즈니스 폼.",
        "여러 `pages/`에서 재사용.",
    ),
    "frontend/src/components/cards": (
        "카드형 **요약 UI**.",
        "차트 축 설정(그건 `charts/`).",
        "추천·로드맵 카드.",
    ),
    "frontend/src/components/charts": (
        "**차트·시각화** 래퍼.",
        "데이터 페칭(그건 `api/` 또는 `features/`).",
        "접근성·반응형은 `FEATURE_SPEC` 정렬.",
    ),
    "frontend/src/components/forms": (
        "입력 **폼** 공통 컴포넌트.",
        "API 스키마 단일 정의는 서버·`API_SPEC`와 동기화.",
        "`pages/`·`features/`에서 재사용.",
    ),
    "frontend/src/components/feedback": (
        "토스트, 스켈레톤, 에러 **피드백** UI.",
        "침묵 실패(항상 envelope 에러 처리와 맞출 것).",
        "`API_SPEC.md` 오류 응답과 사용자 메시지 매핑.",
    ),
    "frontend/src/features/risk-stage": (
        "위험군 단계 **도메인 로직·훅**.",
        "API 라우트 정의.",
        "`risk_stage_service` 계약과 맞춤.",
    ),
    "frontend/src/features/recommendation": (
        "추천 결과 **상태·요청** 캡슐.",
        "서버 후보 산출 알고리즘.",
        "`pages/Recommendation`, `recommendation_service` API.",
    ),
    "frontend/src/features/roadmap": (
        "로드맵 **표현·단계 매핑**.",
        "일정 데이터 수집.",
        "`pages/Roadmap`, `roadmap_service` 계약.",
    ),
    "frontend/src/features/schedule": (
        "일정 feature 자리. **reserved**.",
        "가짜 일정 데이터를 확정처럼 표시.",
        "실연동 시 `schedule_service`·`FEATURE_SPEC.md` 갱신 후 활성화.",
    ),
    "frontend/src/api": (
        "백엔드 **HTTP 클라이언트**·베이스 URL.",
        "Pydantic 모델(그건 `backend/`).",
        "`API_SPEC.md` 엔드포인트·envelope.",
    ),
    "frontend/src/hooks": (
        "공용 **React hooks**.",
        "페이지 전용 일회성 훅(가까운 `pages/`에 둘 수 있음).",
        "`api/`·`store`와 조합해 데이터 페칭 패턴을 맞춘다.",
    ),
    "frontend/src/store": (
        "클라이언트 **전역 상태**.",
        "서버 캐시 진실 공급원(React Query 등 도입 시 분리).",
        "URL·세션과 동기화가 필요한 상태만 유지.",
    ),
    "frontend/src/types": (
        "프론트 **타입 정의**.",
        "`shared/types`와 중복 시 하나로 합칠 것.",
        "`API_SPEC.md` 응답 스키마와 필드명을 맞춘다.",
    ),
    "frontend/src/utils": (
        "순수 **유틸** 함수.",
        "비즈니스 규칙 전부(그건 `features/`).",
        "테스트하기 쉬운 순수 함수로 유지.",
    ),
    "frontend/src/constants": (
        "UI 라벨·경로 상수 등.",
        "taxonomy 허용 값(그건 `data/taxonomy` + 서버 검증).",
        "라우트 경로는 `App`·라우터 설정과 일치.",
    ),
    "frontend/src/styles": (
        "전역 **CSS**·토큰.",
        "컴포넌트 스코프 스타일은 가능하면 컴포넌트 근처.",
        "`main.tsx`에서 import 여부를 유지.",
    ),
    "frontend/tests": (
        "프론트 **단위·통합 테스트**.",
        "E2E 스크린샷 대용량 아티팩트(`.gitignore` 검토).",
        "`npm test` / Vitest 등 도입 시 이 디렉터리를 진입으로 쓴다.",
    ),
}


def main() -> None:
    for rel, (p, a, l) in SPECS.items():
        path = ROOT / rel
        path.mkdir(parents=True, exist_ok=True)
        (path / "FOLDER.md").write_text(block(rel, p, a, l), encoding="utf-8")
    print(f"Wrote {len(SPECS)} FOLDER.md files under {ROOT}")


if __name__ == "__main__":
    main()
