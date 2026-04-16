import os
import pandas as pd
import json
import hashlib
from datetime import datetime

# Paths
BASE_DIR = r"C:\Users\min00\OneDrive\바탕 화면\시스템 분석 2학기\vulnerable_groups_RAG"
MASTER_DIR = os.path.join(BASE_DIR, "data", "processed", "master")
RELATION_DIR = os.path.join(BASE_DIR, "data", "canonical", "relations")
OUT_DIR = os.path.join(BASE_DIR, "data", "canonical", "candidates")

os.makedirs(OUT_DIR, exist_ok=True)

def generate_content_hash(data_dict):
    """Generates a SHA256 hash of the dictionary content."""
    # Sort keys to ensure consistent hashing
    encoded = json.dumps(data_dict, sort_keys=True, ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

def main():
    print("Starting Phase 4: Candidate Generation...")

    # 1. Load Master Data
    cert_master_path = os.path.join(MASTER_DIR, "cert_master.csv")
    if not os.path.exists(cert_master_path):
        print(f"Error: {cert_master_path} not found.")
        return
    df_cert = pd.read_csv(cert_master_path)
    print(f"Loaded {len(df_cert)} certificates from master.")

    # 2. Load Relations
    # Aliases
    alias_path = os.path.join(MASTER_DIR, "cert_alias.csv")
    df_alias = pd.read_csv(alias_path) if os.path.exists(alias_path) else pd.DataFrame(columns=['cert_id', 'alias'])
    alias_map = df_alias.groupby('cert_id')['alias'].apply(list).to_dict()

    # Domains
    domain_mapping_path = os.path.join(RELATION_DIR, "cert_domain_mapping.csv")
    df_domain = pd.read_csv(domain_mapping_path)
    primary_domain_map = df_domain[df_domain['is_primary'] == True].set_index('cert_id')['domain_sub_label_id'].to_dict()
    # Fallback for primary domain if no is_primary=True exists for some reason
    all_primary_candidates = df_domain.groupby('cert_id')['domain_sub_label_id'].first().to_dict()
    
    related_domains_map = df_domain.groupby('cert_id')['domain_sub_label_id'].apply(list).to_dict()

    # Jobs
    job_mapping_path = os.path.join(RELATION_DIR, "cert_job_mapping.csv")
    df_job = pd.read_csv(job_mapping_path) if os.path.exists(job_mapping_path) else pd.DataFrame(columns=['cert_id', 'job_role_id'])
    related_jobs_map = df_job.groupby('cert_id')['job_role_id'].apply(list).to_dict()

    # Roadmap Stages
    roadmap_mapping_path = os.path.join(RELATION_DIR, "cert_to_roadmap_stage.csv")
    df_roadmap = pd.read_csv(roadmap_mapping_path)
    roadmap_stages_map = df_roadmap.groupby('cert_id')['roadmap_stage_id'].apply(list).to_dict()

    # Majors
    major_mapping_path = os.path.join(RELATION_DIR, "cert_major_mapping.csv")
    major_master_path = os.path.join(MASTER_DIR, "major_master.csv")
    if os.path.exists(major_mapping_path) and os.path.exists(major_master_path):
        df_cmm = pd.read_csv(major_mapping_path)
        df_mm = pd.read_csv(major_master_path)
        major_name_map = df_mm.set_index('major_id')['major_name'].to_dict()
        # Group major IDs by cert_id and map to names
        cert_majors = df_cmm.groupby('cert_id')['major_id'].apply(lambda x: [major_name_map.get(mid, mid) for mid in x]).to_dict()
    else:
        cert_majors = {}

    # Jobs (Enriching job names)
    job_master_path = os.path.join(MASTER_DIR, "job_master.csv")
    if os.path.exists(job_master_path):
        df_jm = pd.read_csv(job_master_path)
        job_name_lookup = df_jm.set_index('job_role_id')['job_role_name'].to_dict()
    else:
        job_name_lookup = {}

    # 3. Process candidates
    candidates = []
    updated_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Risk stage recommendation logic (Heuristic based on Tier)
    tier_to_risk_stages = {
        '1_기능사': ['risk_0001', 'risk_0002', 'risk_0003', 'risk_0004', 'risk_0005'],
        '2_산업기사': ['risk_0001', 'risk_0002', 'risk_0003', 'risk_0004'],
        '3_기사': ['risk_0001', 'risk_0002', 'risk_0003'],
        '4_기술사': ['risk_0001', 'risk_0002'],
        '5_기능장': ['risk_0001'],
        '': ['risk_0001', 'risk_0002', 'risk_0003', 'risk_0004']
    }

    for idx, row in df_cert.iterrows():
        cert_id = str(row['cert_id'])
        cert_name = str(row['cert_name'])
        tier = str(row.get('cert_grade_tier', ''))
        if tier == 'nan': tier = ''
        
        # Primary Domain
        p_domain = primary_domain_map.get(cert_id, all_primary_candidates.get(cert_id, "domain_unknown"))
        
        # Related Domains
        r_domains = related_domains_map.get(cert_id, [p_domain])
        
        # Related Jobs
        r_job_ids = related_jobs_map.get(cert_id, [])
        r_job_names = [job_name_lookup.get(jid, jid) for jid in r_job_ids]
        
        # Related Majors
        r_majors = cert_majors.get(cert_id, [])
        
        # Roadmap Stages
        r_stages = roadmap_stages_map.get(cert_id, [])
        
        # Recommended Risk Stages
        rec_risk = tier_to_risk_stages.get(tier, tier_to_risk_stages[''])
        
        # Aliases
        aliases = alias_map.get(cert_id, [])
        
        # Text for Dense (Summary)
        issuer = str(row.get('issuer', ''))
        if issuer == 'nan': issuer = 'Unknown'
        
        desc_parts = [f"{cert_name} ({issuer})."]
        if tier:
            desc_parts.append(f"등급: {tier}.")
        if r_job_names:
            desc_parts.append(f"관련 직무: {', '.join(r_job_names)}.")
        if r_majors:
            desc_parts.append(f"관련 학과: {', '.join(r_majors)}.")
        
        # Backfilled Exam Info
        diff = str(row.get('exam_difficulty', ''))
        if diff and diff != 'nan':
            desc_parts.append(f"시험 난이도: {diff}.")
            
        subj = str(row.get('exam_subject_info', ''))
        if subj and subj != 'nan':
            desc_parts.append(f"시험 과목: {subj}.")
            
        freq = str(row.get('exam_frequency', ''))
        if freq and freq != 'nan':
            desc_parts.append(f"시험 일정: {freq}.")

        desc = " ".join(desc_parts)
        
        # Text for Sparse (Keywords)
        sparse_text = f"{cert_name} {' '.join(aliases)} {' '.join(r_job_names)} {' '.join(r_majors)}"
        
        candidate_row = {
            'row_type': 'certificate_candidate',
            'candidate_id': f"cand_{cert_id}",
            'cert_id': cert_id,
            'cert_name': cert_name,
            'aliases': aliases,
            'issuer': issuer,
            'primary_domain': p_domain,
            'related_domains': r_domains,
            'related_jobs': r_job_ids,
            'related_majors': r_majors,
            'recommended_risk_stages': rec_risk,
            'roadmap_stages': r_stages,
            'text_for_dense': desc,
            'text_for_sparse': sparse_text,
            'valid_from': row.get('valid_from', None),
            'valid_to': row.get('valid_to', None),
            'source_ids': [str(row.get('source', 'master'))],
            'quality_flags': {},
            'updated_at': updated_at
        }
        
        # Content Hash
        candidate_row['content_hash'] = generate_content_hash(candidate_row)
        
        candidates.append(candidate_row)


    # 4. Save to CSV
    df_cand = pd.DataFrame(candidates)
    
    # Convert lists to strings for CSV storage
    df_cand_csv = df_cand.copy()
    for col in ['aliases', 'related_domains', 'related_jobs', 'related_majors', 'recommended_risk_stages', 'roadmap_stages', 'source_ids']:
        df_cand_csv[col] = df_cand_csv[col].apply(lambda x: json.dumps(x, ensure_ascii=False))
    df_cand_csv['quality_flags'] = df_cand_csv['quality_flags'].apply(lambda x: json.dumps(x))

    out_csv = os.path.join(OUT_DIR, "cert_candidates.csv")
    df_cand_csv.to_csv(out_csv, index=False, encoding='utf-8-sig')
    print(f"Saved {len(df_cand)} candidates to {out_csv}.")

    # 5. Save to JSONL
    out_jsonl = os.path.join(OUT_DIR, "cert_candidates.jsonl")
    with open(out_jsonl, 'w', encoding='utf-8') as f:
        for cand in candidates:
            f.write(json.dumps(cand, ensure_ascii=False) + '\n')
    print(f"Saved {len(df_cand)} candidates to {out_jsonl}.")

if __name__ == "__main__":
    main()
