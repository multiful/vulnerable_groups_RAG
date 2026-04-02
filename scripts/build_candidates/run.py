# File: run.py
# Last Updated: 2026-04-03
# Content Hash: SHA256:TBD
# Role: recommendation candidate row 빌드 진입 스텁
from __future__ import annotations


def main() -> None:
    print(
        "build_candidates: entity/relation에서 candidate JSONL을 쓰는 배치는 후속 구현."
    )
    print(
        "형식: DATA_SCHEMA.md §9.1 / data/canonical/candidates/candidates.jsonl.example"
    )
    print(
        "API: POST /api/v1/recommendations 가 CANDIDATES_JSONL_RELATIVE(기본 위 경로)를 읽는다."
    )


if __name__ == "__main__":
    main()
