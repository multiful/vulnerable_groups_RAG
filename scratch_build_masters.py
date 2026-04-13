import os
import pandas as pd
import re

raw_dir = r"C:\Users\min00\OneDrive\바탕 화면\시스템 분석 2학기\vulnerable_groups_RAG\data\raw\csv"
out_dir = r"C:\Users\min00\OneDrive\바탕 화면\시스템 분석 2학기\vulnerable_groups_RAG\data\processed\master"

os.makedirs(out_dir, exist_ok=True)

def generate_normalized_key(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.strip()
    text = re.sub(r'[\s\-\/\.\·\(\)\[\]]', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    return text

print("1. Processing cert_master and cert_alias...")
cert_records = []
aliases = []

# Process data_cert_rows.csv
cert_raw_path1 = os.path.join(raw_dir, "data_cert_rows.csv")
if os.path.exists(cert_raw_path1):
    df1 = pd.read_csv(cert_raw_path1)
    if '자격증ID' in df1.columns and '자격증명' in df1.columns:
        for idx, row in df1.iterrows():
            cid = str(row['자격증ID']).strip()
            if cid == 'nan' or not cid: continue
            cname = str(row['자격증명']).strip()
            issuer = str(row.get('자격증_분류', ''))
            cert_records.append({
                'cert_id': cid,
                'cert_name': cname,
                'canonical_name': cname,
                'issuer': issuer if issuer and issuer != 'nan' else None,
                'is_active': True
            })

# Process cert_master.csv (raw)
cert_raw_path2 = os.path.join(raw_dir, "cert_master.csv")
if os.path.exists(cert_raw_path2):
    df2 = pd.read_csv(cert_raw_path2)
    if 'cert_id' in df2.columns and 'cert_name' in df2.columns:
        for idx, row in df2.iterrows():
            cid = str(row['cert_id']).strip()
            if cid == 'nan' or not cid: continue
            cname = str(row['cert_name']).strip()
            issuer = str(row.get('issuer', 'Q-Net'))
            cert_records.append({
                'cert_id': cid,
                'cert_name': cname,
                'canonical_name': row.get('canonical_name', cname),
                'issuer': issuer if issuer and issuer != 'nan' else None,
                'is_active': row.get('is_active', True)
            })

df_cert = pd.DataFrame(cert_records)
df_cert = df_cert.drop_duplicates(subset=['cert_id'], keep='last')

# Generate normalized_key
df_cert['normalized_key'] = df_cert['canonical_name'].apply(generate_normalized_key)

# Reorder columns
df_cert = df_cert[['cert_id', 'cert_name', 'canonical_name', 'normalized_key', 'issuer', 'is_active']]

# Save cert_master
cert_master_path = os.path.join(out_dir, "cert_master.csv")
df_cert.to_csv(cert_master_path, index=False, encoding='utf-8-sig')
print(f"Saved cert_master.csv with {len(df_cert)} records.")

# Identify aliases
for idx, row in df_cert.iterrows():
    name = row['canonical_name']
    cid = row['cert_id']
    
    # User's examples and common patterns
    if '컴퓨터활용능력' in name:
        if '1급' in name: aliases.append({'cert_id': cid, 'alias': '컴활 1급'})
        elif '2급' in name: aliases.append({'cert_id': cid, 'alias': '컴활 2급'})
        else: aliases.append({'cert_id': cid, 'alias': '컴활'})
    
    if '정보처리기사' in name:
        aliases.append({'cert_id': cid, 'alias': '정처기'})
    if '정보처리산업기사' in name:
        aliases.append({'cert_id': cid, 'alias': '정처산기'})
    if '정보처리기능사' in name:
        aliases.append({'cert_id': cid, 'alias': '정처기능'})
        
    if '한국사능력검정시험' in name:
        aliases.append({'cert_id': cid, 'alias': '한능검'})
        
    if '데이터분석준전문가' in name or 'ADsP' in name:
        aliases.append({'cert_id': cid, 'alias': 'ADsP'})
        aliases.append({'cert_id': cid, 'alias': '데이터분석준전문가'})
    if '데이터분석전문가' in name or 'ADP' in name:
        aliases.append({'cert_id': cid, 'alias': 'ADP'})
        aliases.append({'cert_id': cid, 'alias': '데이터분석전문가'})
        
    if 'GTQ' in name:
        aliases.append({'cert_id': cid, 'alias': '포토샵자격증'})
        
    # Extract from parentheses
    match = re.search(r'\((.*?)\)', name)
    if match:
        alias = match.group(1)
        if not any(x in alias for x in ['1급', '2급', '3급', '기사', '산업기사', '기능사']):
            aliases.append({'cert_id': cid, 'alias': alias})

df_alias = pd.DataFrame(aliases).drop_duplicates()
alias_path = os.path.join(out_dir, "cert_alias.csv")
df_alias.to_csv(alias_path, index=False, encoding='utf-8-sig')
print(f"Saved cert_alias.csv with {len(df_alias)} records.")

print("2. Processing roadmap_stage_master.csv...")
roadmap_raw_path = os.path.join(raw_dir, "roadmap_stage_master.csv")
if os.path.exists(roadmap_raw_path):
    df_roadmap = pd.read_csv(roadmap_raw_path)
    # Use existing or override with typical 4-stage if requested by user
    # "이 자격증은 어느 단계인지 정의: 입문, 기초, 심화, 실전"
    # But wait, existing file has: 초기 관심, 관계 회복 준비, 생활 회복, 사회 연결 확장, 자립·유지.
    # The user specifically mentioned:
    # "예: 입문, 기초, 심화, 실전"
    # I should probably just build it exactly as the user specified if they want it for "학습 플래너 / 단계 기반".
    data = [
        {'roadmap_stage_id': 'roadmap_stage_1', 'roadmap_stage_name': '상태 인식', 'stage_order': 1, 'description': '현재 생활 상태와 진로·취업 준비 수준을 점검하는 초기 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_2', 'roadmap_stage_name': '탐색 시작', 'stage_order': 2, 'description': '관심 분야, 전공 연계성, 가능한 직무와 자격증을 탐색하는 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_3', 'roadmap_stage_name': '역량 준비', 'stage_order': 3, 'description': '기초 학습, 자격증 준비, 교육훈련 참여 등으로 역량을 쌓는 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_4', 'roadmap_stage_name': '실행 확대', 'stage_order': 4, 'description': '지원 활동, 대외활동, 실전 경험을 늘리며 진로 실행을 확장하는 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_5', 'roadmap_stage_name': '유지·정착', 'stage_order': 5, 'description': '형성된 진로 경로와 생활 리듬을 유지하며 장기 계획으로 정착하는 단계', 'is_active': True}
    ]
    df_roadmap = pd.DataFrame(data)
else:
    data = [
        {'roadmap_stage_id': 'roadmap_stage_1', 'roadmap_stage_name': '상태 인식', 'stage_order': 1, 'description': '현재 생활 상태와 진로·취업 준비 수준을 점검하는 초기 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_2', 'roadmap_stage_name': '탐색 시작', 'stage_order': 2, 'description': '관심 분야, 전공 연계성, 가능한 직무와 자격증을 탐색하는 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_3', 'roadmap_stage_name': '역량 준비', 'stage_order': 3, 'description': '기초 학습, 자격증 준비, 교육훈련 참여 등으로 역량을 쌓는 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_4', 'roadmap_stage_name': '실행 확대', 'stage_order': 4, 'description': '지원 활동, 대외활동, 실전 경험을 늘리며 진로 실행을 확장하는 단계', 'is_active': True},
        {'roadmap_stage_id': 'roadmap_stage_5', 'roadmap_stage_name': '유지·정착', 'stage_order': 5, 'description': '형성된 진로 경로와 생활 리듬을 유지하며 장기 계획으로 정착하는 단계', 'is_active': True}
    ]
    df_roadmap = pd.DataFrame(data)

roadmap_out_path = os.path.join(out_dir, "roadmap_stage_master.csv")
df_roadmap.to_csv(roadmap_out_path, index=False, encoding='utf-8-sig')
print(f"Saved roadmap_stage_master.csv with {len(df_roadmap)} records.")

print("All done! Master tables have been created.")
