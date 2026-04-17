import pandas as pd

BASE = r"C:\Users\min00\OneDrive\바탕 화면\시스템 분석 2학기\vulnerable_groups_RAG"

# B-6: roadmap_stage_master.csv 검수
print("=== B-6: roadmap_stage_master.csv 검수 ===")
df = pd.read_csv(f"{BASE}\\data\\processed\\master\\roadmap_stage_master.csv", encoding="utf-8-sig")
print(f"총 행 수: {len(df)}")
print(f"컬럼: {list(df.columns)}")
print()
print("stage_order 오름차순 확인:", list(df["stage_order"]) == sorted(df["stage_order"]))
print("stage_order 연속성 확인:", list(df["stage_order"]) == list(range(1, len(df)+1)))
print()
for col in df.columns:
    nulls = df[col].isna().sum()
    if nulls > 0:
        print(f"  {col}: {nulls}개 결측")
if df.isna().sum().sum() == 0:
    print("  결측치 없음 (OK)")
print()
print("roadmap_stage_id 유일성:", df["roadmap_stage_id"].is_unique)
print()
print(df.to_string(index=False))
print()

# B-7: risk_stage_to_roadmap_stage.csv 검수
print("=== B-7: risk_stage_to_roadmap_stage.csv 검수 ===")
df_rel = pd.read_csv(f"{BASE}\\data\\canonical\\relations\\risk_stage_to_roadmap_stage.csv", encoding="utf-8-sig")
print(f"총 행 수: {len(df_rel)}")
print(f"컬럼: {list(df_rel.columns)}")
print()

df_risk = pd.read_csv(f"{BASE}\\data\\processed\\master\\risk_stage_master.csv", encoding="utf-8-sig")
valid_risk_ids = set(df_risk["risk_stage_id"])
valid_roadmap_ids = set(df["roadmap_stage_id"])
rel_risk = set(df_rel["risk_stage_id"])
rel_roadmap = set(df_rel["roadmap_stage_id"])

print(f"risk_stage_id 참조 정합성: {rel_risk.issubset(valid_risk_ids)}")
print(f"roadmap_stage_id 참조 정합성: {rel_roadmap.issubset(valid_roadmap_ids)}")
print()

all_risk_mapped = valid_risk_ids.issubset(rel_risk)
print(f"모든 risk_stage 매핑 여부: {all_risk_mapped}")
missing = valid_risk_ids - rel_risk
if missing:
    print(f"  미매핑 risk_stage: {missing}")
print()
print(df_rel.to_string(index=False))
