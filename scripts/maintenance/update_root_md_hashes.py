# Content Hash: SHA256:0f867eb82567273375412be03ab67b330cb96a3ff69ac96dbc1445b952f66bd9
# Role: recompute root-level *.md document hash lines (metadata block only; before first "## ").
from __future__ import annotations

import hashlib
from pathlib import Path


def _metadata_end(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("###"):
            return i
    return len(lines)


def body_sha256(lines: list[str]) -> str:
    end = _metadata_end(lines)
    prefix = lines[:end]
    rest = lines[end:]
    prefix_kept = [
        ln
        for ln in prefix
        if "> **문서 해시**:" not in ln and "> **최종 수정일**:" not in ln
    ]
    body = "\n".join(prefix_kept + rest)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def apply(root: Path) -> None:
    for path in sorted(root.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        lines = raw.splitlines()
        h = body_sha256(lines)
        end = _metadata_end(lines)
        if end == 0:
            print(f"skip (no body): {path.name}")
            continue
        meta = lines[:end]
        rest = lines[end:]
        new_meta: list[str] = []
        replaced = False
        for line in meta:
            if "> **문서 해시**:" in line:
                new_meta.append(f"> **문서 해시**: SHA256:{h}")
                replaced = True
            else:
                new_meta.append(line)
        if not replaced:
            out_meta: list[str] = []
            inserted = False
            for line in meta:
                out_meta.append(line)
                if not inserted and "> **최종 수정일**:" in line:
                    out_meta.append(f"> **문서 해시**: SHA256:{h}")
                    inserted = True
            if inserted:
                new_meta = out_meta
                replaced = True
        if not replaced:
            print(f"skip (no date in metadata): {path.name}")
            continue
        path.write_text("\n".join(new_meta + rest) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
        print(f"{path.name}\t{h}")


if __name__ == "__main__":
    apply(Path(__file__).resolve().parents[2])
