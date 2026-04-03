# Content Hash: SHA256:d5517d8785ed05c3c42857d599fbdb6fd114c4a33a5dafeea70150a27c78503f
# Role: domain_v2 / prefer_job 텍스트에서 세부 라벨(줄 시작 "- ") 추출
from __future__ import annotations

from pathlib import Path


def labels_from_taxonomy_file(path: Path) -> set[str]:
    """`domain_v2.txt`, `prefer_job.txt` 형식: 본문에 `- 세부라벨` 행이 섞여 있다."""
    if not path.is_file():
        return set()
    out: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s.startswith("- "):
            label = s[2:].strip()
            if label:
                out.add(label)
    return out
