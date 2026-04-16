import os
import pandas as pd
import re

# Base paths
BASE_DIR = r"C:\Users\min00\OneDrive\바탕 화면\시스템 분석 2학기\vulnerable_groups_RAG"
RAW_CSV = os.path.join(BASE_DIR, "data", "raw", "csv", "ncs_mapping_rows.csv")
CERT_MASTER = os.path.join(BASE_DIR, "data", "processed", "master", "cert_master.csv")
MAJOR_MASTER = os.path.join(BASE_DIR, "data", "processed", "master", "major_master.csv")
OUT_FILE = os.path.join(BASE_DIR, "data", "canonical", "relations", "cert_major_mapping.csv")

os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)

def generate_normalized_key(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.strip()
    # Replace separators with underscore
    text = re.sub(r'[\s\-\/\.\·\ㆍ\(\)\[\]]', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    return text

def main():
    print("Starting Step 3-3: Building cert_major_mapping.csv...")

    # 1. Load Cert Master
    if not os.path.exists(CERT_MASTER):
        print(f"Error: {CERT_MASTER} not found.")
        return
    df_cert = pd.read_csv(CERT_MASTER)
    # Map both original name and normalized key to cert_id for better matching
    cert_name_map = df_cert.set_index('cert_name')['cert_id'].to_dict()
    cert_norm_map = df_cert.set_index('normalized_key')['cert_id'].to_dict()

    # 2. Load Major Master
    if not os.path.exists(MAJOR_MASTER):
        print(f"Error: {MAJOR_MASTER} not found.")
        return
    df_major = pd.read_csv(MAJOR_MASTER)
    major_map = df_major.set_index('normalized_key')['major_id'].to_dict()
    # Also map direct name just in case
    major_name_map = df_major.set_index('major_name')['major_id'].to_dict()

    # 3. Load NCS Mapping Rows
    if not os.path.exists(RAW_CSV):
        print(f"Error: {RAW_CSV} not found.")
        return
    
    # Try different encodings
    try:
        df_ncs = pd.read_csv(RAW_CSV, encoding='utf-8-sig')
    except:
        df_ncs = pd.read_csv(RAW_CSV, encoding='cp949')

    print(f"Loaded {len(df_ncs)} rows from NCS mapping source.")

    relations = []
    skipped_certs = set()
    skipped_majors = set()
    match_count = 0

    for idx, row in df_ncs.iterrows():
        cname = str(row.get('자격증명', '')).strip()
        if not cname or cname == 'nan':
            continue
            
        # Get standardized cert_id
        cid = cert_name_map.get(cname)
        if not cid:
            cid = cert_norm_map.get(generate_normalized_key(cname))
            
        if not cid:
            skipped_certs.add(cname)
            continue

        # Process 학과 (Major) column
        majors_raw = str(row.get('학과', ''))
        if not majors_raw or majors_raw == 'nan':
            continue

        # Split by various delimiters
        # Note: Some names might contain dots or slashes, but usually they separate majors here.
        # But we must be careful not to split "3D모델링/운용" if it were in the source.
        # Typically the separator in ncs_mapping_rows is comma, dot, or slash.
        major_candidates = re.split(r'[,.\/ㆍ\s]+', majors_raw)
        
        for m_raw in major_candidates:
            m_raw = m_raw.strip()
            if not m_raw:
                continue
            
            mid = major_name_map.get(m_raw)
            if not mid:
                mid = major_map.get(generate_normalized_key(m_raw))
            
            if mid:
                relations.append({
                    'cert_id': cid,
                    'major_id': mid,
                    'is_active': True
                })
                match_count += 1
            else:
                skipped_majors.add(m_raw)

    # Convert to DataFrame and remove duplicates
    df_rel = pd.DataFrame(relations)
    if not df_rel.empty:
        df_rel = df_rel.drop_duplicates()
        # Add relation_id
        df_rel.insert(0, 'relation_id', [f'cmj_{i+1:05d}' for i in range(len(df_rel))])
        
        # Save to CSV
        df_rel.to_csv(OUT_FILE, index=False, encoding='utf-8-sig')
        print(f"Saved {len(df_rel)} relations to {OUT_FILE}.")
    else:
        print("No relations were created.")

    print(f"Matched relations: {match_count}")
    print(f"Skipped Certs count: {len(skipped_certs)}")
    print(f"Skipped Majors count (unique): {len(skipped_majors)}")
    if skipped_certs:
        print(f"Sample skipped certs: {list(skipped_certs)[:5]}")
    if skipped_majors:
        print(f"Sample skipped majors: {list(skipped_majors)[:5]}")

if __name__ == "__main__":
    main()
