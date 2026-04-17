# audit_integrity.md

> **파일명**: audit_integrity.md
> **최종 수정일**: 2026-04-18
> **문서 해시**: SHA256:TBD
> **문서 역할**: 추천 파이프라인 데이터 무결성 감사 결과 (2026-04-18)
> **문서 우선순위**: reference

---

## 1. 감사 범위

- `data/processed/master/cert_master.csv` (1,290행)
- `data/canonical/candidates/cert_candidates.jsonl` (1,290행)
- 참조 마스터: `domain_master.csv`, `job_master.csv`, `risk_stage_master.csv`, `roadmap_stage_master.csv`

---

## 2. Taxonomy ID 정합성 — ✅ CLEAN

| 필드 | 위반 건수 |
|---|---|
| `related_domains` | **0** |
| `related_jobs` | **0** |
| `recommended_risk_stages` | **0** |
| `roadmap_stages` | **0** |

→ 모든 ID가 마스터 파일에 정의된 값만 사용. 추가 조치 불필요.

---

## 3. 합격률(`avg_pass_rate_3yr`) 누락 현황 — ⚠️ 주의

| cert_grade_tier | 전체 | 누락 | 누락률 | 영향 |
|---|---|---|---|---|
| 빈값(비기술자격) | 572 | 182 | 31.8% | 키워드 fallback 적용 |
| 1_기능사 | 243 | 86 | 35.4% | 키워드 fallback 적용 |
| 2_산업기사 | 217 | 102 | **47.0%** | ⚠️ tier 기반 고정(level=20) |
| 3_기사 | 131 | 16 | 12.2% | tier 기반 고정(level=30) |
| 4_기술사 | 89 | 1 | 1.1% | tier 기반 고정(level=40) |
| 5_기능장 | 38 | 9 | 23.7% | tier 기반 고정(level=45) |
| **합계** | **1,290** | **396** | **30.7%** | — |

### 영향 분석

- **기술자격 (tier 존재)**: `cert_grade_tier`가 1순위이므로 pass_rate 누락이 단계 배치에 영향 없음.
  단, **동일 tier 내 정렬** 시 pass_rate가 없으면 `0.0`으로 처리 → 해당 자격증이 동 tier 내 뒤로 밀림.
- **비기술자격 (tier 빈값)**: pass_rate 2순위 → 없으면 키워드 3순위 fallback → 정확도 저하 위험.
  특히 **2_산업기사(47% 누락)**가 tier 우선이지만, 비기술자격 중 pass_rate 없는 182건은 품질 위험.

### 권고 (데이터팀)

- `exam_pass_rate` 컬럼 보강 진행 중 (698/1,290 채워짐)
- 비기술자격 pass_rate 누락 182건: 수동 수집 또는 Q-Net 크롤링 필요
- 2_산업기사 pass_rate 누락 102건: `data_cert_rows.csv` 재확인 권장

---

## 4. 추천 파이프라인 영향 요약

| 시나리오 | 현재 동작 | 권장 조치 |
|---|---|---|
| 기술자격 pass_rate 누락 | tier 우선이므로 단계 배치 정상 — 동 tier 내 정렬만 부정확 | 데이터 보강 시 자동 개선 |
| 비기술자격 pass_rate 누락 | 키워드 fallback → 자격증명에 "전문가"/"1급" 등 없으면 기본값(stage_0002) | 키워드 규칙 점검 필요 |
| Taxonomy 위반 | 없음 | 현 상태 유지 |

---

## 5. 감사 도구

```bash
# 재실행 명령 (프로젝트 루트에서)
python scripts/test_recommendation.py   # 로드맵 순서 무결성 포함
```
