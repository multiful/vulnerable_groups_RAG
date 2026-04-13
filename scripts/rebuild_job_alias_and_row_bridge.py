# -*- coding: utf-8 -*-
"""job_raw_merged_rows 기준으로 job_alias_mapping + 행→alias 브리지 재생성."""
from __future__ import annotations

import csv
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "data" / "raw" / "csv" / "job_raw_merged_rows.csv"
JOB_MASTER = ROOT / "data" / "processed" / "master" / "job_master.csv"
OUT_ALIAS = ROOT / "data" / "processed" / "mappings" / "job_alias_mapping.csv"
OUT_BRIDGE = ROOT / "data" / "processed" / "mappings" / "job_row_alias_bridge.csv"
LEGACY_BRIDGE = ROOT / "data" / "processed" / "mappings" / "job_info_job_mapping.csv"


@dataclass
class JobRow:
    job_role_id: str
    job_role_name: str
    normalized_key: str


def normalize_key(s: str) -> str:
    """DATA_SCHEMA 3.7과 동일한 보조 키."""
    if not s:
        return ""
    t = unicodedata.normalize("NFKC", s).strip().lower()
    for ch in ("ㆍ", "·", "•"):
        t = t.replace(ch, "_")
    t = re.sub(r"[\s/\\.\-,:;|()[\]{}]+", "_", t)
    t = re.sub(r"[^\w가-힣_]+", "_", t, flags=re.UNICODE)
    t = re.sub(r"_+", "_", t).strip("_")
    return t


def job_fragments(job: JobRow) -> list[str]:
    parts: set[str] = set()
    for chunk in re.split(r"[/,\s]+", job.job_role_name):
        nk = normalize_key(chunk)
        if len(nk) >= 2:
            parts.add(nk)
    if job.normalized_key:
        parts.add(job.normalized_key)
    return sorted(parts, key=len, reverse=True)


# (부분문자열, job_role_id) — 긴 키를 먼저 검사하도록 정렬해 두고 싶지만, 아래에서 길이순 정렬
# 넓은 귀속(검수 권장). `auto_fallback`으로 표시한다.
_FALLBACK_NEEDLE_TO_JOB: list[tuple[str, str]] = [
    ("조작원", "job_0037"),
    ("제조원", "job_0037"),
    ("조립원", "job_0037"),
    ("성형기", "job_0037"),
    ("압연원", "job_0037"),
    ("충전원", "job_0037"),
    ("제작원", "job_0037"),
    ("검사원", "job_0039"),
    ("도장원", "job_0035"),
    ("수리원", "job_0035"),
    ("설치", "job_0035"),
    ("a/s", "job_0035"),
    ("디자이너", "job_0120"),
    ("디자인", "job_0120"),
    ("목공", "job_0034"),
    ("가구", "job_0034"),
    ("가죽", "job_0132"),
    ("가수", "job_0131"),
    ("개그", "job_0131"),
    ("연예", "job_0131"),
    ("촬영", "job_0126"),
    ("모델", "job_0125"),
    ("학자", "job_0083"),
    ("전문가", "job_0083"),
    ("간병", "job_0087"),
    ("도우미", "job_0119"),
    ("가정부", "job_0119"),
    ("승무원", "job_0063"),
    ("갑판", "job_0060"),
    ("견적", "job_0052"),
    ("경제", "job_0083"),
    ("사육", "job_0136"),
    ("축산", "job_0136"),
    ("한복", "job_0132"),
    ("간판", "job_0120"),
    ("건전지", "job_0037"),
    ("operation research", "job_0083"),
    ("재배", "job_0133"),
    ("재배자", "job_0133"),
    ("재배원", "job_0133"),
    ("광고", "job_0077"),
    ("작가", "job_0128"),
    ("구성", "job_0128"),
    ("극작가", "job_0128"),
    ("기자", "job_0126"),
    ("연주", "job_0131"),
    ("국악", "job_0131"),
    ("게이머", "job_0015"),
    ("게임", "job_0015"),
    ("경매", "job_0086"),
    ("매표", "job_0074"),
    ("계산원", "job_0074"),
    ("교도", "job_0082"),
    ("국회의원", "job_0082"),
    ("광산", "job_0138"),
    ("채석", "job_0138"),
    ("금속", "job_0034"),
    ("구매", "job_0080"),
    ("분석가", "job_0001"),
    ("임원", "job_0073"),
    ("공장", "job_0036"),
    ("반장", "job_0036"),
    ("기술자", "job_0037"),
    ("선별", "job_0133"),
    ("절단", "job_0037"),
    ("용해", "job_0037"),
    ("배관", "job_0047"),
    ("굴진", "job_0138"),
    ("궤도", "job_0055"),
    ("세공", "job_0130"),
    ("도금", "job_0037"),
    ("주조", "job_0037"),
    ("제관", "job_0037"),
    ("극판", "job_0032"),
    ("조종", "job_0037"),
    ("사령", "job_0020"),
    ("고위", "job_0073"),
    ("문 작성", "job_0128"),
    ("제도사", "job_0120"),
    ("아티스트", "job_0125"),
    ("사진작가", "job_0124"),
    ("미화", "job_0035"),
    ("닦이", "job_0119"),
    ("작물", "job_0133"),
    ("마무리", "job_0037"),
    ("관세", "job_0079"),
    ("구두", "job_0132"),
    ("금형", "job_0034"),
    ("기전", "job_0030"),
    ("연마", "job_0037"),
    ("낙농", "job_0136"),
    ("농림", "job_0133"),
    ("농촌지도", "job_0103"),
    ("시험원", "job_0039"),
    ("프로듀서", "job_0126"),
    ("앵커", "job_0126"),
    ("다이어트", "job_0119"),
    ("운전원", "job_0065"),
    ("트럭", "job_0065"),
    ("덤프", "job_0065"),
    ("도배", "job_0048"),
    ("도살", "job_0136"),
    ("도축", "job_0136"),
    ("도선", "job_0060"),
    ("도자기", "job_0130"),
    ("동물", "job_0117"),
    ("조련", "job_0117"),
    ("더빙", "job_0126"),
    ("녹음", "job_0126"),
    ("동시녹음", "job_0126"),
    ("캐스팅", "job_0125"),
    ("디렉터", "job_0126"),
    ("개발원", "job_0037"),
    ("라디오", "job_0126"),
    ("레미콘", "job_0047"),
    ("대통령", "job_0082"),
    ("화물차", "job_0065"),
    ("단열", "job_0047"),
    ("단조", "job_0037"),
    ("담금질", "job_0037"),
    ("담배", "job_0111"),
    ("도공", "job_0047"),
    ("독서지도", "job_0102"),
    ("부화", "job_0136"),
    ("래핑", "job_0037"),
    ("레이들", "job_0037"),
    ("레카", "job_0065"),
    ("네이미", "job_0115"),
    ("냉동", "job_0037"),
    ("압연", "job_0037"),
    ("드라마", "job_0126"),
    ("뉴스", "job_0126"),
]

_KEYWORD_OVERRIDES: list[tuple[str, str]] = [
    ("공인회계사", "job_0067"),
    ("회계사", "job_0067"),
    ("세무사", "job_0066"),
    ("변리사", "job_0084"),
    ("변호사", "job_0084"),
    ("법무", "job_0084"),
    ("간호", "job_0087"),
    ("물리치료", "job_0100"),
    ("작업치료", "job_0100"),
    ("방사선", "job_0091"),
    ("약사", "job_0091"),
    ("한약사", "job_0091"),
    ("수의사", "job_0117"),
    ("의사", "job_0091"),
    ("전문의", "job_0091"),
    ("치과", "job_0091"),
    ("한의사", "job_0091"),
    ("응급구조", "job_0093"),
    ("119구조", "job_0093"),
    ("소방", "job_0042"),
    ("경찰", "job_0082"),
    ("군인", "job_0139"),
    ("군무원", "job_0139"),
    ("교수", "job_0101"),
    ("교사", "job_0101"),
    ("강사", "job_0101"),
    ("유치원", "job_0101"),
    ("사회복지", "job_0094"),
    ("상담", "job_0095"),
    ("직업상담", "job_0097"),
    ("청소년지도", "job_0096"),
    ("사서", "job_0101"),
    ("연구원", "job_0083"),
    ("개발자", "job_0012"),
    ("프로그래머", "job_0012"),
    ("소프트웨어", "job_0012"),
    ("백엔드", "job_0009"),
    ("프론트", "job_0010"),
    ("풀스택", "job_0011"),
    ("데이터분석", "job_0001"),
    ("데이터 분석", "job_0001"),
    ("데이터 과학", "job_0003"),
    ("머신러닝", "job_0006"),
    ("딥러닝", "job_0006"),
    ("인공지능", "job_0005"),
    ("클라우드", "job_0023"),
    ("devops", "job_0024"),
    ("정보보안", "job_0025"),
    ("보안", "job_0025"),
    ("네트워크", "job_0022"),
    ("시스템 운영", "job_0020"),
    ("dba", "job_0026"),
    ("회계", "job_0067"),
    ("세무", "job_0066"),
    ("재무", "job_0068"),
    ("금융", "job_0069"),
    ("은행", "job_0069"),
    ("보험", "job_0071"),
    ("감정평가", "job_0086"),
    ("부동산", "job_0085"),
    ("인사", "job_0075"),
    ("총무", "job_0076"),
    ("노무", "job_0075"),
    ("마케팅", "job_0077"),
    ("영업", "job_0078"),
    ("무역", "job_0079"),
    ("물류", "job_0080"),
    ("유통", "job_0081"),
    ("품질관리", "job_0039"),
    ("생산관리", "job_0036"),
    ("생산기술", "job_0037"),
    ("기계", "job_0034"),
    ("전기", "job_0030"),
    ("전자", "job_0031"),
    ("반도체", "job_0032"),
    ("설비", "job_0044"),
    ("환경", "job_0043"),
    ("안전", "job_0041"),
    ("건축", "job_0046"),
    ("토목", "job_0049"),
    ("실내건축", "job_0048"),
    ("측량", "job_0051"),
    ("gis", "job_0051"),
    ("조경", "job_0050"),
    ("도시계획", "job_0050"),
    ("철도", "job_0055"),
    ("자동차", "job_0058"),
    ("선박", "job_0060"),
    ("항공", "job_0063"),
    ("조리", "job_0108"),
    ("제과", "job_0109"),
    ("제빵", "job_0109"),
    ("바리스타", "job_0110"),
    ("영양", "job_0112"),
    ("식품", "job_0111"),
    ("디자인", "job_0120"),
    ("ux", "job_0121"),
    ("ui", "job_0121"),
    ("편집", "job_0122"),
    ("영상", "job_0124"),
    ("방송", "job_0126"),
    ("콘텐츠", "job_0125"),
    ("3d", "job_0127"),
    ("인쇄", "job_0129"),
    ("출판", "job_0129"),
    ("음악", "job_0131"),
    ("공연", "job_0131"),
    ("패션", "job_0132"),
    ("농업", "job_0133"),
    ("스마트팜", "job_0134"),
    ("축산", "job_0136"),
    ("수산", "job_0137"),
    ("산림", "job_0135"),
    ("광업", "job_0138"),
    ("미용", "job_0114"),
    ("헤어", "job_0114"),
    ("메이크업", "job_0115"),
    ("피부", "job_0116"),
    ("호텔", "job_0105"),
    ("관광", "job_0106"),
    ("여행", "job_0107"),
    ("스포츠", "job_0118"),
    ("운동", "job_0119"),
    ("반려동물", "job_0117"),
    ("게임", "job_0015"),
    ("임베디드", "job_0018"),
    ("모바일", "job_0013"),
    ("웹", "job_0012"),
    ("테스트", "job_0019"),
    ("qa", "job_0019"),
    ("기상", "job_0083"),
    ("예보", "job_0083"),
    ("검침", "job_0044"),
    ("계기", "job_0044"),
    ("의료장비", "job_0091"),
    ("안경", "job_0091"),
    ("임상", "job_0091"),
    ("병원", "job_0089"),
    ("의무기록", "job_0090"),
    ("보건의료정보", "job_0088"),
    ("복지행정", "job_0098"),
    ("사례관리", "job_0099"),
    ("행정", "job_0082"),
    ("공무원", "job_0082"),
    ("공공", "job_0082"),
    ("정책", "job_0083"),
    ("평가", "job_0083"),
    ("컨설턴트", "job_0073"),
    ("컨설팅", "job_0073"),
    ("번역", "job_0104"),
    ("통역", "job_0106"),
    ("한국어교육", "job_0104"),
    ("평생교육", "job_0102"),
    ("직업교육", "job_0103"),
    ("외식", "job_0113"),
    ("erp", "job_0073"),
    ("cctv", "job_0025"),
]


def load_jobs() -> list[JobRow]:
    rows: list[JobRow] = []
    with JOB_MASTER.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(
                JobRow(
                    job_role_id=r["job_role_id"].strip(),
                    job_role_name=r["job_role_name"].strip(),
                    normalized_key=r["normalized_key"].strip(),
                )
            )
    return rows


def map_raw_to_job(raw_display: str, nk: str, jobs: list[JobRow]) -> tuple[str, str, float | None, str | None]:
    """(job_role_id, match_status, match_score, matched_job_role_name) — 항상 job_role_id 반환."""
    # 1) 정확 일치
    for j in jobs:
        if nk == j.normalized_key:
            return j.job_role_id, "auto_exact", 1.0, j.job_role_name

    # 2) 키워드 오버라이드 (원문·정규화 모두에서 부분일치, 긴 키 우선)
    hay_norm = nk
    hay_raw = raw_display.lower()
    best_kw: tuple[int, str, str] | None = None  # (-len, job_id, name)
    for needle, jid in sorted(_KEYWORD_OVERRIDES, key=lambda x: -len(x[0])):
        n = needle.lower()
        if n in hay_raw or normalize_key(needle) in hay_norm:
            jname = next((x.job_role_name for x in jobs if x.job_role_id == jid), "")
            keylen = len(needle)
            cand = (-keylen, jid, jname)
            if best_kw is None or cand < best_kw:
                best_kw = cand
    if best_kw:
        _, jid, jname = best_kw
        return jid, "auto_keyword", 0.9, jname

    # 3) 직무명/조각이 raw 정규화 키에 포함 (가장 긴 조각 우선, 동률이면 스킵)
    best_sub: list[tuple[int, str, str]] = []
    best_len = 0
    for j in jobs:
        for frag in job_fragments(j):
            if len(frag) < 2:
                continue
            if frag in nk:
                L = len(frag)
                if L > best_len:
                    best_len = L
                    best_sub = [(L, j.job_role_id, j.job_role_name)]
                elif L == best_len:
                    best_sub.append((L, j.job_role_id, j.job_role_name))
    if best_len >= 2 and len({x[1] for x in best_sub}) == 1:
        jid, jname = best_sub[0][1], best_sub[0][2]
        return jid, "auto_substring", min(0.85, 0.5 + best_len * 0.02), jname

    # 4) fuzzy: 직무명과의 유사도
    best_ratio = 0.0
    second = 0.0
    best_j: JobRow | None = None
    for j in jobs:
        r = SequenceMatcher(None, raw_display, j.job_role_name).ratio()
        if r > best_ratio:
            second = best_ratio
            best_ratio = r
            best_j = j
        elif r > second:
            second = r
    if best_j and best_ratio >= 0.42 and (best_ratio - second) >= 0.04:
        return best_j.job_role_id, "auto_fuzzy", round(best_ratio, 4), best_j.job_role_name

    # 5) 역방향: raw 정규화 키가 어떤 직무 정규화 키에 포함(길이≥4), 후보 1개일 때만
    if len(nk) >= 4:
        rev = [j for j in jobs if nk in j.normalized_key]
        if len(rev) == 1:
            j = rev[0]
            return j.job_role_id, "auto_substring_rev", min(0.82, 0.45 + len(nk) * 0.02), j.job_role_name

    # 6) 넓은 fallback (taxonomy에 세목이 없을 때 상위 직무군으로 귀속)
    hay_raw = raw_display.lower()
    best_fb: tuple[int, str, str] | None = None
    for needle, jid in sorted(_FALLBACK_NEEDLE_TO_JOB, key=lambda x: -len(x[0])):
        if needle.lower() in hay_raw or normalize_key(needle) in nk:
            jname = next((x.job_role_name for x in jobs if x.job_role_id == jid), "")
            cand = (-len(needle), jid, jname)
            if best_fb is None or cand < best_fb:
                best_fb = cand
    if best_fb:
        _, jid, jname = best_fb
        return jid, "auto_fallback", 0.35, jname

    # 7) taxonomy에 세목이 없는 직종 — 플래그용 기본 귀속(추천 로직에서 가중치 낮추거나 제외 가능)
    catch = next((x for x in jobs if x.job_role_id == "job_0074"), jobs[0])
    return catch.job_role_id, "auto_catchall", 0.05, catch.job_role_name


def main() -> None:
    jobs = load_jobs()
    # nk -> {variants set, sources set, primary_name}
    bucket: dict[str, dict] = defaultdict(lambda: {"variants": set(), "sources": set(), "primary": None})

    with MERGED.open(encoding="utf-8-sig", newline="") as f:
        merged_rows = list(csv.DictReader(f))

    for row in merged_rows:
        src = (row.get("source_dataset") or "").strip()
        name = (row.get("raw_job_name") or "").strip()
        if name:
            nk = normalize_key(name)
            if not nk:
                continue
            b = bucket[nk]
            b["variants"].add(name)
            if src:
                b["sources"].add(src)
            if b["primary"] is None:
                b["primary"] = name
        aliases = (row.get("raw_job_aliases") or "").strip()
        if aliases:
            for part in re.split(r"[,|]", aliases):
                t = part.strip()
                if not t:
                    continue
                nk = normalize_key(t)
                if not nk:
                    continue
                b = bucket[nk]
                b["variants"].add(t)
                if src:
                    b["sources"].add(src)
                if b["primary"] is None:
                    b["primary"] = t

    sorted_nks = sorted(bucket.keys())
    nk_to_ja: dict[str, str] = {}
    alias_rows: list[dict] = []

    for i, nk in enumerate(sorted_nks, start=1):
        ja_id = f"ja_{i:04d}"
        nk_to_ja[nk] = ja_id
        info = bucket[nk]
        variants = sorted(info["variants"], key=lambda s: (len(s), s))
        primary = info["primary"] or variants[0]
        alternates = [v for v in variants if v != primary]
        sources = ";".join(sorted(info["sources"])) if info["sources"] else "job_raw_merged_rows"

        jid, status, score, jname = map_raw_to_job(primary, nk, jobs)

        alias_rows.append(
            {
                "job_alias_id": ja_id,
                "raw_job_name": primary,
                "alternate_raw_labels": " | ".join(alternates) if alternates else "",
                "normalized_key": nk,
                "job_role_id": jid,
                "match_status": status,
                "source_dataset": sources,
                "is_active": "TRUE",
                "match_score": "" if score is None else str(score),
                "matched_job_role_name": jname or "",
            }
        )

    with OUT_ALIAS.open("w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "job_alias_id",
            "raw_job_name",
            "alternate_raw_labels",
            "normalized_key",
            "job_role_id",
            "match_status",
            "source_dataset",
            "is_active",
            "match_score",
            "matched_job_role_name",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(alias_rows)

    bridge: list[dict] = []
    for idx, row in enumerate(merged_rows, start=1):
        name = (row.get("raw_job_name") or "").strip()
        nk = normalize_key(name)
        ja = nk_to_ja.get(nk, "")
        bridge.append(
            {
                "relation_id": f"jrb_{idx:04d}",
                "source_dataset": (row.get("source_dataset") or "").strip(),
                "source_row_id": (row.get("source_row_id") or "").strip(),
                "jobdic_seq": (row.get("jobdic_seq") or "").strip(),
                "raw_job_name": name,
                "normalized_key": nk,
                "job_alias_id": ja,
            }
        )

    with OUT_BRIDGE.open("w", encoding="utf-8-sig", newline="") as f:
        bf = [
            "relation_id",
            "source_dataset",
            "source_row_id",
            "jobdic_seq",
            "raw_job_name",
            "normalized_key",
            "job_alias_id",
        ]
        w = csv.DictWriter(f, fieldnames=bf)
        w.writeheader()
        w.writerows(bridge)

    if LEGACY_BRIDGE.exists():
        LEGACY_BRIDGE.unlink()

    mapped = sum(1 for r in alias_rows if r["job_role_id"])
    print(
        f"aliases={len(alias_rows)} mapped={mapped} unmapped={len(alias_rows) - mapped} "
        f"bridge_rows={len(bridge)}"
    )


if __name__ == "__main__":
    main()
