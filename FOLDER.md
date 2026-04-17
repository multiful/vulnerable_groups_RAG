---
title: Repository-wide Review (FOLDER.md)
last_reviewed: 2026-04-17
document_hash: SHA256:TBD
agent: copilot-cli-reviewer
format: gemini-friendly
---

Summary

- 목적: 모든 폴더의 MD 메타데이터·구조 및 Python 스크립트(garbage code 후보) 검토. 변경은 절대하지 않음 — 권고만 제공.

Findings (by folder)

1. root
   - 루트 주요 문서들(API_SPEC.md, README.md, PRD.md 등)은 `문서 해시`를 포함하고 있음.
   - `copilot-instructions.md`가 루트에 생성되어 있음 (문서 해시: TBD).

2. scripts/
   - 다수의 사용자용 스크립트에서 print(...)가 광범위하게 사용됨 (예: scripts/*.py, scratch_build_masters.py).
   - 권장: production/automation용은 Python logging으로 전환(레벨·포맷·출력 대상 설정). print는 디버그·비정형 출력을 유발함.

3. backend/
   - 대부분 모듈화되어 있으며 테스트 코드가 존재. 일부 runner/ingest 도구에서 DRY-RUN/CLI 출력용 print 사용 중(허용범위지만 logging 권장).

4. data/raw/
   - 원본 HTML/JS(서드파티 포함)에서 다수의 TODO 주석(특히 jquery 파일). 원본 데이터이므로 검토 제외 권장(민감도/저작권·변경 불필요).

5. docs/ 및 FOLDER.md 전반
   - 많은 하위 폴더에 이미 FOLDER.md가 존재(자동 생성 도구 scripts/maintenance/generate_folder_md.py 참고).
   - 다수의 FOLDER.md는 `문서 해시: SHA256:TBD` (CLAUDE.md 규칙에 합치 — placeholder 허용).

High-severity / Actionable items

- scripts/*.py: 교체 권장 — print -> logging; 적어도 CI/운영 스크립트는 로그 레벨 제어 가능하게 개선할 것. (심각도: 중)
- data/raw/* (third-party JS): 수정하지 말 것. TODO 주석은 원본 보존용이며 검토 대상에서 제외(심각도: 낮)
- 일부 문서의 해시가 TBD인 상태임: 정기적으로 scripts/maintenance/update_root_md_hashes.py로 반영 권장(심각도: 낮)

Recommendations (short)

- 자동화: scripts/maintenance/generate_folder_md.py 와 update_root_md_hashes.py 를 CI(병합 후)로 실행하여 FOLDER.md·루트 해시를 갱신.
- Logging: scripts와 CLI 도구에 Python logging 채택(예시: logger = logging.getLogger(__name__), Handler 설정).
- Exclusions: raw 원본(data/raw)과 vendor 파일은 검사 예외로 처리.

Next steps

- 이 FOLDER.md는 claude가 읽기 쉬운 YAML frontmatter + 명확한 섹션을 포함합니다.
- 원하시면 각 최상위 폴더별로 상세 항목(파일별 문제·라인 예시)을 추가로 생성하겠습니다. (수동 변경 없이 검토·보고만 수행)

Detailed Findings (automated scan)

- Print statements (candidates for replacement by logging):
  - scripts/backfill_cert_master.py
  - scripts/build_all_relations.py
  - scripts/build_cert_candidates.py
  - scripts/build_cert_domain_mapping.py
  - scripts/build_cert_major_mapping.py
  - scripts/build_candidates\run.py
  - scripts/build_entities\run.py
  - scripts/parse\run.py
  - scripts/maintenance\update_root_md_hashes.py
  - scripts/maintenance\generate_folder_md.py
  - scripts/search_chunks.py
  - scripts/test_recommendation.py
  - scratch_build_masters.py
  - backend/rag/pipeline/runner.py
  - backend/rag/ingest/cli.py

  Note: these prints are common in CLI or maintenance scripts — replace with Python logging when used in CI/production to control verbosity and structured outputs.

- TODO markers (actionable/notes):
  - backend/app/services/retrieval_service.py (# TODO reserved: reranker/BM25)
  - EXPERIMENT_GUIDE.md, EVALUATION_GUIDELINE.md, and many data/raw third-party JS files (jquery-*.js) contain TODO comments. Treat third-party/raw files as excluded from edits; track TODOs in project issues if work is required.

- 'pass' usages (may be placeholders):
  - scripts/test_recommendation.py
  - backend/app/services/recommendation_service.py
  - backend/rag/parse/parsers/pdfplumber_parser.py

  These appear to be intentional placeholders or minimal implementations; review for completeness if the module is required in production.

- No matches found for: FIXME, large blocks of commented-out code matching common code patterns, or explicit 'if False' dead branches.

Severity summary

- Medium: print->logging conversion in automation/CI scripts to improve observability and avoid noisy console output.
- Low: TODO markers and pass placeholders — require triage to determine if they represent outstanding work.
- Low/Info: third-party raw files contain many TODOs but should be left untouched.

Recommendations

1. Create a short task list (issues) for: replacing prints in CI/automation scripts with logging, triaging TODOs in backend services, and confirming intent of 'pass' placeholders.
2. Add a CI job to run `python -m pyflakes` or `ruff` to catch unused imports, undefined names, and simple dead code in Python files (exclude data/raw).
3. Continue periodic FOLDER.md updates after triage.

Reviewed-by: copilot-cli (no code changes performed)

