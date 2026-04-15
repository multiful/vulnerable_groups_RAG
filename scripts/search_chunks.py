# Content Hash: SHA256:<AUTO_HASH_OR_TBD>
"""청크 키워드 검색"""
import sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
JSONL = Path("data/index_ready/chunks/chunks.jsonl")
MAX_TEXT = 800

def search(must, boost=[], top_n=5):
    hits = []
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            text = c["text"]
            if not all(t in text for t in must):
                continue
            score = sum(text.count(t) * 3 for t in must) + sum(text.count(t) for t in boost)
            hits.append((score, c))
    hits.sort(key=lambda x: -x[0])
    return hits[:top_n]

hits = search(["항공정비사"], ["응시료", "수수료", "1차"])
if not hits:
    hits = search(["항공정비"], ["응시료", "수수료"])

print(f"히트: {len(hits)}개\n")
for i, (score, c) in enumerate(hits, 1):
    m = c["metadata"]
    print(f"--- #{i} score={score}  {c['doc_id']}  {m['source_loc']} ---")
    print(f"section : {m['section_path']}")
    print(c["text"][:MAX_TEXT])
    print()
