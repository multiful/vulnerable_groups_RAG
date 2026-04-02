# HASH_INCREMENTAL_BUILD_GUIDE.md

> **파일명**: HASH_INCREMENTAL_BUILD_GUIDE.md  
> **최종 수정일**: 2026-04-03  
> **문서 해시**: SHA256:d61fce4efad10029e920cc45129bcd1acf7d95469da8701923d8214e766a37fa
> **문서 역할**: 해시 라인, 증분 빌드, 선택적 재처리, 성능 최적화 규칙 가이드  
> **문서 우선순위**: reference  
> **연관 문서**: CHANGE_CONTROL.md, DATA_SCHEMA.md, RAG_PIPELINE.md, CURSOR_PROJECT_RULES.md  
> **참조 규칙**: md 파일, 스크립트, 파이프라인 단계에 해시 라인과 증분 처리 규칙을 적용할 때 먼저 이 문서를 확인한다.

---

## 1. 문서 목적

이 문서는 **해시 라인(hash line)** 과 **증분 빌드(incremental build)** 규칙을 정의한다.  
목표는 변경되지 않은 문서나 데이터에 대해 불필요한 재처리를 줄이고, 파이프라인 실행 속도를 높이며, Cursor가 새 파일을 만들 때도 같은 규칙을 일관되게 적용하도록 만드는 것이다.

이 문서는 다음을 정의한다.

- md 파일과 스크립트의 해시 라인 형식
- 해시 계산 기준
- 변경 감지 기준
- 단계별 캐시 키 설계
- 선택적 재처리 규칙
- 증분 빌드 전략
- Cursor가 새 파일을 만들 때 따라야 하는 규칙

---

## 2. 왜 해시 라인이 필요한가

해시 라인은 단순한 메타데이터가 아니라, **변경 여부를 빠르게 판단하기 위한 식별자**다.

해시 라인을 도입하면 아래가 가능해진다.

1. 파일 내용이 실제로 바뀌었는지 빠르게 판단
2. 변경되지 않은 파일은 재파싱/재청킹/재임베딩 생략
3. CSV row나 candidate row 단위 증분 재생성
4. 대규모 전체 재처리 대신 변경된 부분만 재처리
5. 캐시 무효화 조건을 명확하게 관리
6. 협업 시 “무엇이 실제로 바뀌었는지”를 쉽게 추적

즉, 해시 라인은 **속도 최적화 + 변경 추적 + 캐시 안정화**를 동시에 지원한다.

---

## 3. 핵심 원칙

1. 모든 새 md 파일에는 상단 메타데이터와 함께 **해시 라인**을 포함한다.
2. 모든 새 스크립트 파일에도 언어별 주석 형식의 **해시 라인**을 포함한다.
3. 해시는 파일의 **실제 의미 내용**이 바뀌었을 때만 바뀌는 것이 이상적이다.
4. `최종 수정일` 같은 휘발성 메타데이터만 바뀐 경우, 필요하면 동일한 body hash를 유지할 수 있어야 한다.
5. 해시 라인은 그 자체를 포함해 다시 계산하지 않는다.
6. 증분 빌드는 항상 “입력 해시 + 버전” 조합으로 결정한다.

---

## 4. md 파일 해시 라인 규칙

## 4.1 권장 메타데이터 형식

모든 md 파일 상단에는 아래 형식을 사용한다.

```md
# FILE_NAME.md

> **파일명**: FILE_NAME.md  
> **최종 수정일**: YYYY-MM-DD  
> **문서 해시**: SHA256:<AUTO_HASH>  
> **문서 역할**: ...  
> **문서 우선순위**: ...  
> **연관 문서**: ...  
> **참조 규칙**: ...
```

## 4.2 위치 규칙
- `문서 해시`는 `최종 수정일` 바로 아래에 둔다.
- 모든 md 파일에서 같은 위치를 유지한다.

## 4.3 계산 규칙
문서 해시는 아래 기준으로 계산하는 것을 권장한다.

- 해시 계산 대상:
  - 본문 전체
  - 제목
  - 구조적 메타데이터
- 해시 계산 제외 대상:
  - `문서 해시` 라인 자체
  - 필요 시 `최종 수정일` 라인

## 4.4 왜 `최종 수정일` 제외가 유용한가
`최종 수정일`까지 해시에 넣으면, 날짜만 바뀌어도 해시가 바뀌고 전체 재처리가 발생할 수 있다.  
속도 최적화 목적이라면 **문서 의미 내용이 바뀌었을 때만 해시가 바뀌는 구조**가 더 유리하다.

---

## 5. 스크립트 파일 해시 라인 규칙

언어별로 주석 형식을 사용한다.

## 5.1 Python
```python
# File: script_name.py
# Last Updated: YYYY-MM-DD
# Content Hash: SHA256:<AUTO_HASH>
# Role: ...
```

## 5.2 JavaScript / TypeScript
```javascript
// File: script_name.ts
// Last Updated: YYYY-MM-DD
// Content Hash: SHA256:<AUTO_HASH>
// Role: ...
```

## 5.3 Shell
```bash
# File: run_job.sh
# Last Updated: YYYY-MM-DD
# Content Hash: SHA256:<AUTO_HASH>
# Role: ...
```

## 5.4 SQL
```sql
-- File: build_candidates.sql
-- Last Updated: YYYY-MM-DD
-- Content Hash: SHA256:<AUTO_HASH>
-- Role: ...
```

## 5.5 계산 규칙
스크립트 해시는 아래를 권장한다.

- 해시 계산 대상:
  - 실행 로직
  - 상수
  - 쿼리 본문
- 해시 계산 제외 대상:
  - `Content Hash` 라인
  - 필요 시 `Last Updated` 라인

---

## 6. 해시 종류를 분리해야 하는 이유

하나의 파일 해시만으로는 충분하지 않은 경우가 많다.  
실무적으로는 아래처럼 해시를 분리하는 것이 좋다.

### 6.1 file_hash
원본 파일 전체 기준 해시

용도:
- 원본 문서가 바뀌었는지 판정
- 원본 CSV가 바뀌었는지 판정

### 6.2 parse_hash
parse 결과물 기준 해시

용도:
- parse 결과가 실제로 달라졌는지 판정
- 읽기 순서 / boilerplate 제거 결과 차이 감지

### 6.3 chunk_hash
chunk 단위 해시

용도:
- chunk 재생성 여부 판단
- chunk별 embedding 재사용 여부 판단

### 6.4 row_hash
CSV row 단위 정규화 결과 해시

용도:
- entity / relation / candidate 증분 재생성

### 6.5 content_hash
정규화된 canonical row 또는 candidate row 기준 해시

용도:
- recommendation candidate row 변경 감지
- downstream 인덱스 업데이트 최소화

### 6.6 embedding_key_hash
임베딩 입력 텍스트 + embedding_version 조합 해시

용도:
- 재임베딩 필요 여부 판단

---

## 7. 단계별 증분 처리 규칙

## 7.1 PDF / HTML ingest
재처리 조건:
- 원본 file_hash 변경
- parser version 변경
- profiling rule 변경

재처리 생략 조건:
- 원본 해시 동일
- parser version 동일
- profiling 조건 동일

## 7.2 Parse
재처리 조건:
- file_hash 변경
- parse rule 변경
- OCR 정책 변경
- fallback 정책 변경

재처리 생략 조건:
- parse_hash 동일

## 7.3 Chunking
재처리 조건:
- parse_hash 변경
- chunk_version 변경
- chunk rule 변경

재처리 생략 조건:
- parse_hash 동일
- chunk_version 동일

## 7.4 Embedding
재처리 조건:
- chunk_hash 변경
- embedding_version 변경
- embedding input prompt 변경

재처리 생략 조건:
- chunk_hash 동일
- embedding_version 동일

## 7.5 CSV canonicalization
재처리 조건:
- CSV file_hash 변경
- schema mapping 변경
- normalization rule 변경
- taxonomy 변경

재처리 생략 조건:
- row_hash 동일
- canonical rule version 동일

## 7.6 Candidate build
재처리 조건:
- entity_hash 변경
- relation_hash 변경
- build rule 변경
- risk/roadmap master 변경

재처리 생략 조건:
- upstream canonical hash 동일
- build_version 동일

---

## 8. 실행 속도를 올리는 핵심 기법 정리

아래 기법들은 이 프로젝트에서 특히 유효하다.

### 8.1 변경 없는 단계 스킵
가장 기본적이고 효과가 큰 기법이다.

예:
- 원본 PDF 안 바뀜 → parse 스킵
- parse 안 바뀜 → chunk 스킵
- chunk 안 바뀜 → embedding 스킵

### 8.2 문서 단위가 아니라 청크 단위 재임베딩
문서 하나가 길더라도, 실제로 바뀐 chunk만 다시 임베딩한다.

효과:
- 임베딩 비용 절감
- 인덱싱 시간 단축

### 8.3 row 단위 canonicalization
CSV 전체를 매번 다시 만드는 대신, 바뀐 row만 재정규화한다.

효과:
- entity / relation build 시간 단축
- candidate rebuild 시간 단축

### 8.4 캐시 키에 버전 포함
해시만 쓰면 규칙이 바뀌었을 때 이전 캐시가 잘못 재사용될 수 있다.  
반드시 아래처럼 쓴다.

- `cache_key = input_hash + rule_version`
- `embedding_key = chunk_hash + embedding_version`

### 8.5 lazy rebuild
정말 필요한 시점까지 재생성을 미룬다.

예:
- reserved 기능은 미리 인덱싱하지 않음
- 실제 사용되는 subset만 먼저 구축

### 8.6 selective invalidation
전체 캐시 삭제 대신 영향을 받는 단계만 무효화한다.

예:
- taxonomy만 바뀜 → candidate build부터 다시
- embedding model만 바뀜 → embedding부터 다시
- parse rule만 바뀜 → parse 이후 단계만 다시

### 8.7 persistent cache
프로세스가 끝나도 남는 캐시를 사용한다.

예:
- `build_manifest.json`
- `embedding_cache.sqlite`
- `chunk_hash_map.json`

### 8.8 deterministic normalization
정규화 결과가 실행마다 달라지면 해시가 흔들린다.  
trim, sort, alias merge 순서 등을 항상 결정적으로 유지해야 한다.

### 8.9 stable ordering
배열이나 relation 출력 순서가 매번 달라지면 내용은 같아도 해시가 달라진다.  
정렬 기준을 고정해야 한다.

### 8.10 expensive stage isolation
느린 단계는 독립적으로 분리한다.

예:
- OCR
- large embedding batch
- reranker preprocessing

---

## 9. 해시 라인과 manifest를 함께 써야 하는 이유

파일 상단 해시 라인만으로는 전체 파이프라인 의존성을 추적하기 어렵다.  
그래서 아래와 같은 manifest를 함께 두는 것이 좋다.

예:
```json
{
  "doc_id": "doc_001",
  "file_hash": "sha256:...",
  "parse_hash": "sha256:...",
  "chunk_version": "v2",
  "embedding_version": "bge-m3-2026-04-03",
  "last_built_at": "2026-04-03T10:00:00"
}
```

### 역할
- 이전 빌드 상태 저장
- 어떤 단계까지 최신인지 추적
- selective rebuild 결정

---

## 10. 추천 manifest 구조

최소 권장 필드:

- `object_id`
- `object_type`
- `source_path`
- `file_hash`
- `upstream_hash`
- `stage_name`
- `stage_version`
- `output_hash`
- `last_built_at`
- `status`

### object_type 예시
- `document`
- `chunk`
- `csv_dataset`
- `canonical_entity`
- `canonical_relation`
- `candidate_row`

---

## 11. Cursor가 따라야 할 해시 규칙

Cursor가 새 md 파일이나 스크립트를 생성할 때는 아래를 따른다.

### 11.1 md 파일 생성 시
- 상단 메타데이터를 반드시 넣는다.
- `문서 해시` 라인을 반드시 넣는다.
- 형식은 모든 md에서 동일하게 유지한다.

### 11.2 스크립트 생성 시
- 파일 상단 주석 메타데이터를 넣는다.
- `Content Hash` 라인을 반드시 넣는다.
- 실행 로직과 메타데이터를 분리한다.

### 11.3 수정 시
- 본문이 바뀌면 해시 라인도 갱신 대상으로 간주한다.
- `최종 수정일`도 함께 갱신한다.
- 내용이 바뀌지 않았다면 날짜만 바꾸는 수정은 지양한다.

---

## 12. 이 프로젝트에 바로 적용하면 좋은 구체 규칙

1. 모든 루트 md 파일에 `문서 해시` 줄 추가
2. 모든 새 Python/TS/SQL 스크립트에 `Content Hash` 줄 추가
3. `chunk_hash`, `content_hash`를 downstream 캐시 키로 사용
4. `embedding_version` 바뀌지 않으면 unchanged chunk 재임베딩 금지
5. `row_hash`가 같으면 entity/relation row 재생성 스킵
6. `candidate content_hash`가 같으면 recommendation index 갱신 스킵
7. OCR는 unchanged scanned page에 재적용 금지
8. parser/chunker rule 변경 시 stage version 올리기
9. build 결과는 manifest로 남기기
10. 전체 rebuild는 마지막 수단으로만 사용

---

## 13. 주의사항

- 해시 라인이 있다고 해서 자동으로 속도가 빨라지는 것은 아니다.
- 해시 라인을 **증분 빌드 규칙**과 같이 써야 의미가 있다.
- 정렬 기준이 흔들리면 해시가 불안정해진다.
- `최종 수정일`까지 해시에 넣을지 여부는 팀 규칙으로 고정해야 한다.
- reserved 기능은 아직 캐시/manifest 설계를 과하게 확장하지 않는다.

---

## 14. 최종 요약

해시 라인은 단순 메타데이터가 아니라,  
**변경 감지 → 선택적 재처리 → 캐시 재사용 → 실행 속도 향상**으로 이어지는 핵심 장치다.

이 문서의 핵심은 아래 두 가지다.

1. **모든 md / 스크립트에 해시 라인 규칙을 강제한다.**
2. **해시를 실제 증분 처리 규칙과 연결해 전체 재처리를 줄인다.**
