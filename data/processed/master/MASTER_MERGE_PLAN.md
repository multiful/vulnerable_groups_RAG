# MASTER_MERGE_PLAN.md

> **파일명**: MASTER_MERGE_PLAN.md
> **최종 수정일**: 2026-04-15
> **문서 해시**: SHA256:TBD
> **문서 역할**: master CSV 체크리스트 — 보강/생성/매핑/candidate 전체 진행 현황
> **문서 우선순위**: reference
> **연관 문서**: DATA_SCHEMA.md, SYSTEM_ARCHITECTURE.md, FEATURE_SPEC.md, DIRECTORY_SPEC.md

---

## 0. 체크리스트 범례

| 기호 | 의미 |
|---|---|
| ✅ | 완료 |
| 🔄 | 진행 중 / 부분 완료 |
| ⬜ | 미착수 (자동 생성 가능) |
| 🖊️ | 미착수 (수동 정의 필요) |
| ❌ | 드롭 / 불필요 |

---

## 1. Master 파일 현황

### 1.1 엔티티 마스터 (processed/master/)

| 파일 | 행 수 | ID 형식 | 상태 | 비고 |
|---|---|---|---|---|
| `cert_master.csv` | 1,290 | cert_0001~ | ✅ | grade_tier 컬럼 추가 완료 |
| `ncs_master.csv` | 261 | ncs_0001~ | ✅ | |
| `domain_master.csv` | 43 | domain_0001~ | ✅ | |
| `job_master.csv` | 142 | job_0001~ | ✅ | |
| `major_master.csv` | 8,113 | major_qnet_XXXX | ✅ | |
| `hosting_org_master.csv` | 61 | hosting_org_0001~ | ✅ | |
| `risk_stage_master.csv` | 5 | risk_0001~ | ✅ | |
| `roadmap_stage_master.csv` | 5 | roadmap_stage_0001~ | ✅ | |
| `cert_alias.csv` | 159 | cert_id 재매핑 완료 | ✅ | 27행 드롭(구형ID) |

### 1.2 cert_master 컬럼 현황

| 컬럼 | 상태 | 비고 |
|---|---|---|
| cert_id | ✅ | cert_0001~ |
| cert_name | ✅ | |
| canonical_name | ✅ | |
| normalized_key | ✅ | |
| aliases | ✅ | |
| issuer | ✅ | 전체 Q-Net |
| is_active | ✅ | |
| cert_type | ✅ | 국가기술자격(748)/국가전문자격(282)/국가민간자격(260) |
| grade_name | ✅ | 원본 등급명 (다양한 형태) |
| **cert_grade_tier** | ✅ | §4.7 기준 — 1_기능사/2_산업기사/3_기사/4_기술사/5_기능장/빈값 |
| primary_domain | ✅ | 숫자코드 (domain_master 세부 매핑 미완) |
| top_domain | ✅ | 9개 대분류 |
| domain_name_raw | ✅ | 54개 소분류 원본값 (578개 빈값) |
| source | ✅ | |
| written_avg_pass_rate | ✅ | |
| practical_avg_pass_rate | ✅ | |
| avg_pass_rate_3yr | ✅ | |
| exam_type, has_written, has_practical, has_interview, difficulty, exam_count_per_year | ⬜ optional | data_cert_rows 병합으로 보강 가능 — Phase 4 비blocking |

---

## 2. 관계(Relation) 파일 현황

### 2.1 자동 생성 완료 (canonical/relations/)

| 파일 | 행 수 | 상태 | 생성 기준 |
|---|---|---|---|
| `cert_prerequisite.csv` | 4,013 | 🔄 | 동일 domain_name_raw 내 grade_tier 단계 연결 (⚠️이슈 §10 참조) |
| `cert_to_roadmap_stage.csv` | 1,290 | ✅ | cert_grade_tier → roadmap_stage 단계 매핑 |
| `cert_domain_mapping.csv` | 1,290 | ✅ | is_primary=True 712행 + fallback 578행 (100% 커버) |
| `major_to_domain.csv` | 5,268 | ✅ | domain_label_candidate → domain_master |

### 2.2 소스 있음 — 생성 완료 / 미생성

| 파일 | 소스 | 커버리지 | 상태 |
|---|---|---|---|
| `cert_ncs_mapping.csv` | ncs_mapping_rows (대+중+소코드 join) | 3,573행 / cert 743/1290 (57.6%) / ncs 248/261 (95.0%) | ✅ |
| `cert_job_mapping.csv` | cert_domain_mapping 경유 domain→job 매핑 | 4,755행 / cert 1212/1290 (94.0%) / job 142/142 (100%) | ✅ |
| `cert_major_mapping.csv` | ncs_mapping_rows.학과 컬럼 | 미생성 | ⬜ |

### 2.3 자동 생성 완료

| 파일 | DATA_SCHEMA | 행 수 | 상태 | 비고 |
|---|---|---|---|---|
| `risk_stage_to_roadmap_stage.csv` | §6.5 | 5 | ✅ | risk별 시작 로드맵 단계 1:1 매핑 |
| `job_to_domain.csv` | §6.7 | 151 | ✅ | job 142/142, domain 42/43 (domain_0028 by design) |
| `risk_stage_to_domain.csv` | §6.4 | — | ❌ 삭제 | risk_stage는 roadmap 시작점만 결정. 도메인은 사용자 관심사 입력으로 결정 — 이 관계는 근거 없음 |

### 2.4 낮음 / Defer 가능 (현재 단계 불필요)

| 파일 | DATA_SCHEMA | 상태 | 판단 근거 |
|---|---|---|---|
| `major_to_job.csv` | §6.6 | ❌ defer | 신뢰할 만한 소스 없음. major→domain→job 간접 경로로 대체 |
| `cert_to_hosting_org.csv` | §6.9 | ❌ defer | cert_master.issuer 텍스트로 현재 단계 표시 충분. hosting_org_master join이 필요해지면 그때 생성 |

---

## 3. cert_grade_tier 매핑 규칙

```
grade_name = '기능사'   → cert_grade_tier = '1_기능사'
grade_name = '산업기사' → cert_grade_tier = '2_산업기사'
grade_name = '기사'     → cert_grade_tier = '3_기사'
grade_name = '기술사'   → cert_grade_tier = '4_기술사'
grade_name = '기능장'   → cert_grade_tier = '5_기능장'
그 외 모든 값          → cert_grade_tier = '' (null 처리)
```

**분포** (총 1,290):
- 빈값(null): 572개 (44%) — 공인/전문직/민간자격 등
- 1_기능사: 243개
- 2_산업기사: 217개
- 3_기사: 131개
- 4_기술사: 89개
- 5_기능장: 38개

---

## 4. cert_to_roadmap_stage 매핑 규칙

```
cert_grade_tier = ''           → roadmap_stage_0002 (탐색 시작)
cert_grade_tier = '1_기능사'   → roadmap_stage_0003 (역량 준비)
cert_grade_tier = '2_산업기사' → roadmap_stage_0004 (실행 확대)
cert_grade_tier = '3_기사'     → roadmap_stage_0004 (실행 확대)
cert_grade_tier = '4_기술사'   → roadmap_stage_0005 (유지·정착)
cert_grade_tier = '5_기능장'   → roadmap_stage_0005 (유지·정착)
```

**분포**:
- roadmap_stage_0002 (탐색 시작): 572개
- roadmap_stage_0003 (역량 준비): 243개
- roadmap_stage_0004 (실행 확대): 348개
- roadmap_stage_0005 (유지·정착): 127개

> roadmap_stage_0001(상태 인식)은 자격증 타겟팅 이전 단계 — cert 미연결

---

## 5. cert_prerequisite 생성 규칙

동일 `domain_name_raw` 안에서 grade_tier 단계별 연결:

```
기능사   → 산업기사 : recommended_prior
기능사   → 기사     : recommended_prior
산업기사 → 기사     : recommended_prior
기사     → 기술사   : prerequisite
기사     → 기능장   : recommended_prior
```

총 **4,013개** 관계 생성 (54개 domain_name_raw 기준)

> ⚠️ 의미 정확도 이슈 §10.1 참조 — domain_name_raw가 coarse해서 무관한 cert 간 연결 발생

---

## 6. cert_domain_mapping 매핑 규칙

`domain_name_raw` → `domain_sub_label_id` 수동 매핑 테이블 (54개 값):

| domain_name_raw | domain_sub_label_id | 도메인명 |
|---|---|---|
| 건설기계운전 | domain_0013 | 자동차/모빌리티정비 |
| 건설배관 | domain_0010 | 건축/실내건축 |
| 건축 | domain_0010 | 건축/실내건축 |
| 경영 | domain_0017 | 경영/사무 |
| 광해방지 | domain_0012 | 환경/안전 |
| 교육.자연.과학.사회과학 | domain_0027 | 교육 |
| 금속.재료 | domain_0007 | 재료/금속 |
| 금형.공작기계 | domain_0006 | 기계/제조 |
| 기계장비설비.설치 | domain_0006 | 기계/제조 |
| 기계제작 | domain_0006 | 기계/제조 |
| 농업 | domain_0038 | 농림/축산/수산 |
| 단조.주조 | domain_0006 | 기계/제조 |
| 도시.교통 | domain_0011 | 토목/측량/공간정보 |
| 도장.도금 | domain_0006 | 기계/제조 |
| 디자인 | domain_0033 | 디자인 |
| 목재.가구.공예 | domain_0035 | 공예/목재/주얼리 |
| 방송 | domain_0034 | 콘텐츠/미디어 |
| 방송.무선 | domain_0004 | 정보통신/무선 (방송통신기사 등 무선통신 자격 포함) |
| 보건.의료 | domain_0023 | 의료/보건 |
| 비파괴검사 | domain_0015 | 비파괴검사/품질검사 |
| 사회복지.종교 | domain_0024 | 사회복지/상담 |
| 생산관리 | domain_0006 | 기계/제조 |
| 섬유 | domain_0032 | 의류/패션제작 |
| 숙박.여행.오락.스포츠 | domain_0029 | 관광/항공/호텔 |
| 식품 | domain_0030 | 조리/식품 |
| 안전관리 | domain_0012 | 환경/안전 |
| 어업 | domain_0038 | 농림/축산/수산 |
| 에너지.기상 | domain_0009 | 에너지/원자력 |
| 영업.판매 | domain_0019 | 영업/CS |
| 용접 | domain_0006 | 기계/제조 |
| 운전.운송 | domain_0040 | 철도/교통운송 |
| 위험물 | domain_0008 | 화학/바이오 |
| 의복 | domain_0032 | 의류/패션제작 |
| 이용.미용 | domain_0031 | 미용/패션 |
| 인쇄.사진 | domain_0034 | 콘텐츠/미디어 |
| 임업 | domain_0038 | 농림/축산/수산 |
| 자동차 | domain_0013 | 자동차/모빌리티정비 |
| 전기 | domain_0005 | 전기/전자 |
| 전자 | domain_0005 | 전기/전자 |
| 정보기술 | domain_0002 | 소프트웨어개발 |
| 제과.제빵 | domain_0030 | 조리/식품 |
| 조경 | domain_0011 | 토목/측량/공간정보 |
| 조리 | domain_0030 | 조리/식품 |
| 조선 | domain_0041 | 선박/해양 |
| 채광 | domain_0039 | 광산 |
| 철도 | domain_0040 | 철도/교통운송 |
| 축산 | domain_0038 | 농림/축산/수산 |
| 토목 | domain_0011 | 토목/측량/공간정보 |
| 통신 | domain_0004 | 정보통신/무선 |
| 판금.제관.새시 | domain_0006 | 기계/제조 |
| 항공 | domain_0042 | 항공/조종 |
| 화공 | domain_0008 | 화학/바이오 |
| 환경 | domain_0012 | 환경/안전 |
| (빈값) | fallback 적용 | 578개: keyword 규칙 567개 + top_domain fallback 11개 (is_primary=False) |

**현재 커버리지**: 1,290/1,290 (100%) — is_primary=True 712행 / keyword fallback 567행 / top_domain fallback 11행  
**생성 스크립트**: `scripts/build_cert_domain_mapping.py`

---

## 7. 파이프라인 4단계 구조

```
Phase 1: Masters        → processed/master/ 엔티티 마스터 완성
Phase 2: Source Mapping → data_cert_rows, ncs_mapping, data_jobs 기반 cert 속성 보강
Phase 3: Relations      → canonical/relations/ 관계 파일 완성
Phase 4: Candidates     → canonical/candidates/ 추천 후보 행 생성
```

> **순서 의존성**: Phase 1 완료 → Phase 2 → Phase 3 → Phase 4  
> 각 Phase 내 개별 Step은 병렬 진행 가능

---

## 8. Phase별 실행 계획

### Phase 1 — Masters (완료 ✅)
- cert_master: 1,290행, cert_grade_tier 포함
- ncs/domain/job/major/org/risk/roadmap_stage 마스터 모두 완료
- cert_alias: 159행 재매핑

### Phase 2 — Source Mapping (보강)

#### Step 2-1 — cert_master 시험 상세 컬럼 보강 ⬜ (optional — Phase 4 비blocking)
- 소스: `raw/csv/data_cert_rows.csv` (1,086행)
- join: cert_name 기준
- 추가 컬럼: exam_type, has_written, has_practical, has_interview, difficulty, exam_count_per_year
- **Phase 4 candidate 생성에 필수 아님** — cert_master 현재 컬럼으로 최소 candidate 생성 가능
- 추천 필터링 품질 향상이 필요해질 때 진행

#### Step 2-2 — cert_domain_mapping 보완 ✅
- 578개 빈값(domain_name_raw 없음) — keyword 규칙 + top_domain fallback으로 전량 처리
- keyword 매핑: 567행 / top_domain fallback: 11행 (모두 is_primary=False)
- 스크립트: `scripts/build_cert_domain_mapping.py`

### Phase 3 — Relations ✅ 핵심 완료 (cert_major_mapping ⬜ 제외)

> **현재 상태**: Phase 4 필수 relation 파일 전체 완료.  
> **미완료**: Step 3-3 cert_major_mapping (Phase 4 비blocking — defer 가능)  
> **Phase 4 진입 가능**: cert_candidates.csv 생성 시작 가능

#### Step 3-1 — cert_ncs_mapping.csv 생성 ✅
- 소스: `raw/csv/ncs_mapping_rows.csv`
- join: cert_name → cert_id (exact → 공백정규화 → alias 3단계), 대+중+소직무코드 → ncs_master ncsID
- 출력: `canonical/relations/cert_ncs_mapping.csv`
- 결과: 3,573행 / cert 743/1,290 (57.6%) / ncs 248/261 (95.0%)
- 매칭 방법: exact(3,357), norm(226), alias(14), 미매칭(222)
- **스크립트**: `scripts/build_all_relations.py`

#### Step 3-2 — cert_job_mapping.csv 생성 ✅
- 소스: `cert_domain_mapping` 경유 (domain_sub_label_id → job_role_id 매핑 테이블)
- join: cert → domain → job (43개 domain → 142개 job, DOMAIN_TO_JOBS 테이블)
- 출력: `canonical/relations/cert_job_mapping.csv`
- 결과: 4,755행 / cert 1,212/1,290 (94.0%) / job 142/142 (100%)
- 미연결 78개: domain_0028 (언어/문서/속기) — job_master 해당 직종 없음 (by design)
- **스크립트**: `scripts/build_all_relations.py`

#### Step 3-3 — cert_major_mapping.csv 생성 ⬜
- 소스: `raw/csv/ncs_mapping_rows.csv` 학과 컬럼
- join: cert_name → cert_id, 학과명 split → major_id
- 출력: `canonical/relations/cert_major_mapping.csv`
- **스크립트**: `scripts/build_cert_major_mapping.py` (미작성 — Phase 4 비blocking)

#### Step 3-4 — risk_stage_to_roadmap_stage.csv ✅
- 결과: 5행
- **스크립트**: `scripts/build_all_relations.py` (build_risk_to_roadmap 함수)
- risk_0001→roadmap_stage_0003, risk_0002/0003→roadmap_stage_0002, risk_0004/0005→roadmap_stage_0001

#### Step 3-5 — risk_stage_to_domain.csv ❌ 삭제
- **설계 결정**: domain은 사용자 관심사 입력으로 결정 — risk_stage→domain 관계는 근거 없음
- **이전 상태**: `scripts/build_all_relations.py`로 215행(5×43) 생성됐으나 설계 검토 후 폐기
- **조치**: 생성 파일 삭제 완료 (§9 참조)

#### Step 3-6 — job_to_domain.csv ✅
- 결과: 151행 / job 142/142, domain 42/43
- **스크립트**: `scripts/build_all_relations.py` (build_job_to_domain 함수)
- domain_0028(언어/문서/속기) 미연결 — by design (job_master에 해당 직종 없음)

### Phase 4 — Candidate Generation ⬜  ← **담당자 직접 구현**

> **진입 조건**: Phase 3 핵심 완료 → ✅ 충족  
> **담당**: 담당자 직접 구현 (`scripts/build_cert_candidates.py`)  
> **이 플랜 범위 외**: Phase 4 이후(추천 엔진 입력) 는 담당자 영역 — 상세 스키마·생성 규칙은 DATA_SCHEMA.md §candidate 참조

---

## 8-S. 스크립트 역할분담 (Phase 1~3 범위)

> Phase 4(candidates) 이후는 담당자 영역 — 이 표에 포함하지 않음

| 스크립트 | 담당 Step | 출력 파일 | 상태 |
|---|---|---|---|
| `scripts/build_cert_domain_mapping.py` | Step 2-2 | `canonical/relations/cert_domain_mapping.csv` | ✅ |
| `scripts/build_all_relations.py` | Step 3-1 | `canonical/relations/cert_ncs_mapping.csv` | ✅ |
| `scripts/build_all_relations.py` | Step 3-2 | `canonical/relations/cert_job_mapping.csv` | ✅ |
| `scripts/build_all_relations.py` | Step 3-4 | `canonical/relations/risk_stage_to_roadmap_stage.csv` | ✅ |
| `scripts/build_all_relations.py` | Step 3-6 | `canonical/relations/job_to_domain.csv` | ✅ |
| `scripts/build_all_relations.py` | Step 3-5 ❌ | `risk_stage_to_domain.csv` | ❌ 폐기 (코드 잔존, 출력 미사용) |
| `scripts/build_cert_major_mapping.py` | Step 3-3 | `canonical/relations/cert_major_mapping.csv` | ⬜ 미작성 (비blocking) |
| `scratch_build_masters.py` | Phase 1 전체 | `processed/master/*.csv` | ✅ |

> `build_all_relations.py`의 risk_stage_to_domain 코드는 폐기됐으나 삭제 전 주석 유지.  
> 실제 삭제는 코드 정리 시점에 진행.

---

## 9. 생성 완료 파일 목록 (canonical/relations/)

```
canonical/relations/
├── cert_prerequisite.csv           🔄  4,013행 (⚠️cross-domain 이슈)
├── cert_to_roadmap_stage.csv       ✅  1,290행
├── cert_domain_mapping.csv         ✅  1,290행 (is_primary=T 712 / fallback 578)
├── major_to_domain.csv             ✅  5,268행
├── cert_ncs_mapping.csv            ✅  3,573행 (cert 57.6% / ncs 95.0%)  ⚠️소수 NCS 소스 오류 있음
├── cert_job_mapping.csv            ✅  4,755행 (cert 94.0% / job 100%)
├── job_to_domain.csv               ✅    151행 (job 100% / domain 42/43)
├── risk_stage_to_roadmap_stage.csv ✅      5행
├── risk_stage_to_domain.csv        ❌  삭제 — 설계 근거 없음 (domain은 사용자 관심사로 결정)
├── cert_major_mapping.csv          ⬜  미생성
├── major_to_job.csv                ❌  defer
└── cert_to_hosting_org.csv         ❌  defer

canonical/candidates/
└── cert_candidates.csv             ⬜  Phase 4 다음 단계 ← 지금 진입 가능
```

---

## 10. 매핑 정확도 이슈

### 10.1 cert_prerequisite — cross-domain 연결 문제 (🔄 수용가능 / 개선 고려)

**문제**: `domain_name_raw`가 coarse해서 동일 도메인 라벨 안에 서로 무관한 자격증이 묶임

**실제 사례** (`토목` 도메인, 692개 연결):
```
콘크리트산업기사 → 항로표지기능사   [recommended_prior]  ← 무관
콘크리트산업기사 → 잠수기능사        [recommended_prior]  ← 무관
측량기사         → 토목시공기술사    [prerequisite]       ← 정상
```

**영향 범위**: 토목(692), 기계장비설비.설치(677), 건축(357) — 대형 도메인일수록 심각

**현재 결정**: `recommended_prior` 관계는 필터링/활용 시 도메인 일치 여부를 2차 체크  
**개선안 (optional)**: `domain_name_raw` + `grade_name` 기반 서브그루핑으로 재생성

### 10.2 cert_domain_mapping — fallback 완료 ✅

**해결**: `scripts/build_cert_domain_mapping.py`로 keyword 규칙(567행) + top_domain fallback(11행) 적용  
**결과**: 1,290/1,290 (100%) 커버, is_primary=False 행은 domain_name_raw 미존재 자격 표시

**주요 수정 이력**:
- `방송.무선` → domain_0004 (정보통신/무선)으로 수정 (기존 domain_0034 오류)
- `원자로조종사면허` → domain_0009 (에너지/원자력), 규칙 순서 조정으로 해결
- `전산회계운용사` → domain_0016 (금융/회계), domain_0002 오분류 수정

### 10.3 cert_job_mapping — 94% 커버 완료 ✅

**결과**: 4,755행 / cert 1,212/1,290 (94.0%) / job 142/142 (100%)  
**미연결 78개**: domain_0028 (언어/문서/속기) — job_master에 해당 직종 없음 (정상, by design)

### 10.4 data_cert_rows 미매핑 11개 T-prefix 자격증

**원인**: data_cert_rows에 있으나 cert_master에 없는 11개 (모두 국가기술자격)

| ID | 자격증명 | 비고 |
|---|---|---|
| T107 | 통신선로산업기사 | |
| T302 | 농기계정비기능사 | |
| T576 | 임상심리사 1급 | |
| T577 | 임상심리사 2급 | |
| T601 | 재료조직평가산업기사 | |
| T625 | 전자계산기기사 | 폐지 가능성 |
| T627 | 전자계산기제어산업기사 | 폐지 가능성 |
| T628 | 전자계산기조직응용기사 | 폐지 가능성 |
| T634 | 전자부품장착산업기사 | 폐지 가능성 |
| T659 | 통신기기기능사 | |
| T663 | 통신선로기능사 | |

**결정 필요**: Q-Net에서 폐지 확인 후 cert_master 추가 또는 제외

---

## 11. 새로운 CSV 입력 처리 절차

> 새 소스 CSV가 추가되거나 기존 CSV가 업데이트될 때 파이프라인이 끊기지 않도록 하는 절차

### 11.1 새 자격증 원본 CSV 추가 시 (raw/csv/cert_master.csv 갱신)

1. `raw/csv/cert_master.csv` 업데이트 (새 행 append 또는 기존 행 수정)
2. `processed/master/cert_master.csv` 재생성 스크립트 실행
   - 새 행만 cert_0XXX ID 부여 (기존 ID 불변)
   - cert_grade_tier 자동 도출
   - file_hash 비교 → 변경 행만 처리
3. cert_alias.csv: 영향받는 cert_name 재매핑 확인
4. Phase 3 relations: 새 cert_id 포함하여 selective 재생성
   - cert_to_roadmap_stage: 새 행 append
   - cert_domain_mapping: domain_name_raw 있으면 append
   - cert_prerequisite: 해당 domain_name_raw 전체 재생성
5. Phase 4 candidates: 새 cert_id만 candidate row 생성

### 11.2 새 매핑 소스 CSV 추가 시 (ncs_mapping, data_jobs 등)

1. `raw/csv/` 에 새 파일 추가
2. MASTER_MERGE_PLAN.md §8 Phase 3에 신규 Step 추가
3. 매핑 스크립트 작성: cert_name/ncsID → 새 ID 체계 join
4. 출력: `canonical/relations/{새파일}.csv`
5. candidate row content_hash 비교 후 영향 cert만 재생성

### 11.3 domain_master / job_master 갱신 시

1. 새 domain_id / job_id 부여 (기존 ID 불변)
2. 영향받는 relation 파일만 selective 재생성
3. MASTER_MERGE_PLAN.md §6 매핑 테이블 업데이트
4. candidate row에서 domain_ids_all 변경된 cert만 재생성

### 11.4 파이프라인 버전 관리 규칙

| 변경 사항 | 올려야 할 버전 | 재처리 범위 |
|---|---|---|
| cert_grade_tier 규칙 변경 | `rule_version` | 전체 cert_to_roadmap_stage, cert_prerequisite |
| roadmap_stage 매핑 변경 | `rule_version` | cert_to_roadmap_stage 전체 |
| domain_name_raw 매핑 테이블 변경 | `rule_version` | cert_domain_mapping 전체 |
| cert_master 행 추가 | — | 새 행만 증분 처리 |
| cert_master 행 수정 | — | 해당 cert_id만 재처리 |

---

## 12. 미해결 이슈 (우선순위순)

| 우선순위 | 이슈 | 내용 | 다음 액션 |
|---|---|---|---|
| ~~높음~~ ✅ | cert_domain_mapping 578개 빈값 | keyword+fallback으로 해소 (1290/1290) | 완료 |
| ~~높음~~ ✅ | cert_ncs_mapping 미생성 | 3,573행 생성 완료 | 완료 |
| ~~높음~~ ✅ | cert_job_mapping 미생성 | 4,755행 생성 완료 (94%) | 완료 |
| **CRITICAL** | risk_stage_to_roadmap_stage 수동 정의 없음 | 위험군 기반 추천 경로 완전 차단 | §13 참조 |
| **CRITICAL** | risk_stage_to_domain 수동 정의 없음 | 위험군 기반 도메인 필터링 불가 | §13 참조 |
| **CRITICAL** | job_to_domain 수동 정의 없음 | 역방향 job→domain 조회 불가 | §13 참조 |
| 중간 | cert_ncs_mapping 미연결 547개 | NCS 없는 cert 42.4% — 국가전문/민간자격 위주 | 허용 가능 (NCS 분류 없는 자격 정상) |
| 중간 | cert_major_mapping 미생성 | major→cert 추천 경로 단절 | Step 3-3 실행 |
| 중간 | cert_master 시험 상세 컬럼 미보강 | exam_type/difficulty 등 6개 컬럼 빈값 | Step 2-1 실행 |
| 중간 | cert_prerequisite cross-domain | 토목/기계 등 대형 domain에서 무관 cert 연결 | 개선안 검토 |
| 낮음 | T-prefix 11개 미매핑 | 폐지 여부 확인 후 cert_master 추가/제외 결정 | 수동 확인 |
| 낮음 | primary_domain 숫자코드 | cert_master.primary_domain ↔ domain_master 매핑 미완 | 필요시 처리 |

---

## 13. 병목 분석 (2026-04-15 기준)

### 13.1 추천 가능 범위

| 조건 | 대상 cert 수 | 비율 | 비고 |
|---|---|---|---|
| domain + roadmap_stage 연결 (최소) | 1,290 / 1,290 | 100% | candidate 생성 가능 |
| domain + job + roadmap_stage 연결 (풀조건) | 1,212 / 1,290 | 94.0% | 78개 domain_0028 제외 (by design) |
| NCS 연결 | 743 / 1,290 | 57.6% | NCS 없는 전문/민간자격은 정상 |

### 13.2 CRITICAL 병목 — ✅ 해소

| 파일 | 상태 |
|---|---|
| `risk_stage_to_roadmap_stage.csv` | ✅ 5행 생성 완료 |
| `job_to_domain.csv` | ✅ 151행 생성 완료 |
| `risk_stage_to_domain.csv` | ❌ 삭제 — 설계상 불필요 (domain은 사용자 관심사 입력으로 결정, risk_stage로 domain을 배정할 근거 없음) |

### 13.3 MODERATE 병목 — 일부 잔여

| 파일 | 영향 | 담당 |
|---|---|---|
| `cert_major_mapping.csv` | 전공 기반 자격증 추천 경로 없음 | Person A (개발) |
| cert_master 시험 상세 컬럼 | difficulty 등 6개 컬럼 미보강 — 추천 자체는 가능, 필터링 품질 향상 시 진행 | Person A (optional) |

### 13.4 간접 연결 현황

| 연결 경로 | 가능 여부 | 방법 |
|---|---|---|
| cert → domain | ✅ | cert_domain_mapping |
| cert → job | ✅ | cert_job_mapping |
| cert → roadmap_stage | ✅ | cert_to_roadmap_stage |
| cert → ncs | ✅ (57.6%) | cert_ncs_mapping |
| cert → major | ❌ | cert_major_mapping 미생성 |
| risk_stage → cert | ❌ | risk_stage_to_domain 수동 정의 필요 |
| job → cert (역방향) | ❌ | job_to_domain 수동 정의 필요 |
| ncs → domain | 간접 | cert 경유 (ncs→cert→domain) |

---

## 14. 2인 업무 분담 (~2026-04-22)

> **역할 기준**  
> - Person A: cert / ncs 관련 master CSV 및 매핑  
> - Person B: major / hosting / risk / roadmap 관련 CSV  

### Person A — cert_candidates 생성 담당 (잔여 작업)

| 순번 | 상태 | 작업 | 대상 파일 |
|---|---|---|---|
| A-1 | ❌ | cert_candidates.csv 생성 스크립트 작성 | `scripts/build_cert_candidates.py` |
| A-2 | ❌ (A-1 의존) | cert_candidates.csv 최초 생성 | `canonical/candidates/cert_candidates.csv` |

**작업 순서**: A-1 → A-2  
**참고**: §8 Phase 4 candidate row 스키마 기준, 1,290행 목표

---

### Person B — cert_major_mapping + cert_master 보강 담당 (신규 배정)

| 순번 | 상태 | 작업 | 대상 파일 |
|---|---|---|---|
| B-1 | ✅ | risk_stage_to_roadmap_stage.csv | `canonical/relations/` 5행 |
| B-2 | ✅ | job_to_domain.csv | `canonical/relations/` 151행 |
| B-3 | ✅ | major_to_domain.csv | `canonical/relations/` 5,268행 |
| B-4 | ❌ | cert_major_mapping.csv 생성 | `canonical/relations/cert_major_mapping.csv` |
| B-5 | 보류 | cert_master 시험 상세 컬럼 보강 | `processed/master/cert_master.csv` |

**B-4 작업 순서**: 독립 진행 가능  
**B-4 참고 소스**: `raw/csv/ncs_mapping_rows.csv` 학과 컬럼 → major_master join  
**B-5**: Phase 4 이후 exam_type 등 6개 컬럼 보강, `raw/csv/data_cert_rows.csv` (1,086행) 참고

---

### 완료 체크포인트

| 체크 | 담당 | 조건 |
|---|---|---|
| cert_major_mapping 생성 | B | 파일 존재, 행 수 > 0 |
| cert_candidates.csv 생성 | A | 1,290행, content_hash 있음 |
| DEV_LOG.md 반영 | A | Phase 3 완료 + Phase 4 착수 기록 |
