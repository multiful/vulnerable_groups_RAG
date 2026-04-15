# Content Hash: SHA256:TBD
# Script: build_all_relations.py
# Purpose: cert_job_mapping(재생성), job_to_domain, risk_stage_to_roadmap_stage 생성
# Note: risk_stage_to_domain 생성 로직은 설계 폐기됨 (2026-04-15) — 아래 Section 5 코드는 실행되나 출력 파일 미사용

import csv, os, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
RELATIONS = os.path.join(BASE, 'canonical', 'relations')

def load(path):
    with open(path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

domains     = load(os.path.join(BASE, 'processed', 'master', 'domain_master.csv'))
jobs        = load(os.path.join(BASE, 'processed', 'master', 'job_master.csv'))
risks       = load(os.path.join(BASE, 'processed', 'master', 'risk_stage_master.csv'))
roadmaps    = load(os.path.join(BASE, 'processed', 'master', 'roadmap_stage_master.csv'))
domain_map  = load(os.path.join(RELATIONS, 'cert_domain_mapping.csv'))

domain_ids  = {r['domain_sub_label_id'] for r in domains}
job_ids     = {r['job_role_id'] for r in jobs}

# ── 1. 올바른 DOMAIN_TO_JOBS (job_master 기준으로 재작성) ────
DOMAIN_TO_JOBS = {
    'domain_0001': ['job_0001','job_0002','job_0003','job_0004','job_0005','job_0006','job_0007','job_0008'],
    'domain_0002': ['job_0009','job_0010','job_0011','job_0012','job_0013','job_0014','job_0015','job_0016','job_0017','job_0018','job_0019'],
    'domain_0003': ['job_0020','job_0021','job_0022','job_0023','job_0024','job_0025','job_0026','job_0029'],
    'domain_0004': ['job_0027','job_0028'],
    'domain_0005': ['job_0030','job_0031','job_0032','job_0033'],
    'domain_0006': ['job_0034','job_0035','job_0036','job_0037','job_0038','job_0039'],
    'domain_0007': ['job_0036','job_0037','job_0039'],
    'domain_0008': ['job_0038','job_0039','job_0043'],
    'domain_0009': ['job_0044','job_0045'],
    'domain_0010': ['job_0046','job_0047','job_0048'],
    'domain_0011': ['job_0049','job_0050','job_0051','job_0052','job_0053'],
    'domain_0012': ['job_0041','job_0043','job_0053'],
    'domain_0013': ['job_0058','job_0059'],
    'domain_0014': ['job_0042'],
    'domain_0015': ['job_0040'],
    'domain_0016': ['job_0066','job_0067','job_0068','job_0069','job_0070','job_0071','job_0072'],
    'domain_0017': ['job_0073','job_0074','job_0075','job_0076','job_0077','job_0078'],
    'domain_0018': ['job_0065','job_0079','job_0080','job_0081'],
    'domain_0019': ['job_0077','job_0078'],
    'domain_0020': ['job_0085','job_0086'],
    'domain_0021': ['job_0082','job_0083'],
    'domain_0022': ['job_0084'],
    'domain_0023': ['job_0087','job_0088','job_0089','job_0090','job_0091','job_0092','job_0093'],
    'domain_0024': ['job_0094','job_0095','job_0096','job_0097','job_0098','job_0099'],
    'domain_0025': ['job_0100','job_0118','job_0119'],
    'domain_0026': ['job_0117'],
    'domain_0027': ['job_0101','job_0102','job_0103','job_0104'],
    'domain_0028': [],
    'domain_0029': ['job_0105','job_0106','job_0107'],
    'domain_0030': ['job_0108','job_0109','job_0110','job_0111','job_0112','job_0113'],
    'domain_0031': ['job_0114','job_0115','job_0116'],
    'domain_0032': ['job_0132'],
    'domain_0033': ['job_0120','job_0121','job_0122','job_0123'],
    'domain_0034': ['job_0124','job_0125','job_0126','job_0127','job_0128','job_0129'],
    'domain_0035': ['job_0130'],
    'domain_0036': ['job_0131'],
    'domain_0037': ['job_0054'],
    'domain_0038': ['job_0133','job_0134','job_0135','job_0136','job_0137'],
    'domain_0039': ['job_0138'],
    'domain_0040': ['job_0055','job_0056','job_0057'],
    'domain_0041': ['job_0060','job_0061','job_0062'],
    'domain_0042': ['job_0063','job_0064'],
    'domain_0043': ['job_0139','job_0140','job_0141','job_0142'],
}

# ── 2. cert_job_mapping.csv 재생성 ──────────────────────────
cert_to_domain = {r['cert_id']: r['domain_sub_label_id'] for r in domain_map}
rows_cjm, idx = [], 1
cert_covered, job_covered = set(), set()

for cert_id, domain_id in cert_to_domain.items():
    for job_id in DOMAIN_TO_JOBS.get(domain_id, []):
        if job_id not in job_ids:
            print(f'[WARN] {job_id} not in job_master', file=sys.stderr)
            continue
        rows_cjm.append({'relation_id': f'cjm_{idx:05d}', 'cert_id': cert_id,
                          'job_role_id': job_id, 'is_active': 'True'})
        idx += 1
        cert_covered.add(cert_id)
        job_covered.add(job_id)

out = os.path.join(RELATIONS, 'cert_job_mapping.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['relation_id','cert_id','job_role_id','is_active'])
    w.writeheader(); w.writerows(rows_cjm)
no_job = len(cert_to_domain) - len(cert_covered)
print(f'[cert_job_mapping] {len(rows_cjm):,}행  cert {len(cert_covered)}/{len(cert_to_domain)}  job {len(job_covered)}/{len(job_ids)}  미연결cert {no_job}개')

# ── 3. job_to_domain.csv ────────────────────────────────────
job_to_domains = collections.defaultdict(list)
for domain_id, job_list in DOMAIN_TO_JOBS.items():
    for job_id in job_list:
        if domain_id not in job_to_domains[job_id]:
            job_to_domains[job_id].append(domain_id)

rows_jtd, idx = [], 1
for job in sorted(jobs, key=lambda x: x['job_role_id']):
    job_id = job['job_role_id']
    for domain_id in job_to_domains.get(job_id, []):
        rows_jtd.append({'relation_id': f'jtd_{idx:05d}', 'job_role_id': job_id,
                          'domain_sub_label_id': domain_id, 'is_active': 'True'})
        idx += 1

out = os.path.join(RELATIONS, 'job_to_domain.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['relation_id','job_role_id','domain_sub_label_id','is_active'])
    w.writeheader(); w.writerows(rows_jtd)
job_covered_jtd    = {r['job_role_id'] for r in rows_jtd}
domain_covered_jtd = {r['domain_sub_label_id'] for r in rows_jtd}
no_job_jtd = sorted(j['job_role_id'] for j in jobs if j['job_role_id'] not in job_covered_jtd)
print(f'[job_to_domain]    {len(rows_jtd):,}행  job {len(job_covered_jtd)}/{len(job_ids)}  domain {len(domain_covered_jtd)}/{len(domain_ids)}')
if no_job_jtd:
    for jid in no_job_jtd:
        nm = next(j['job_role_name'] for j in jobs if j['job_role_id'] == jid)
        print(f'  미연결 job: {jid} {nm}')

# ── 4. risk_stage_to_roadmap_stage.csv ──────────────────────
RISK_TO_ROADMAP = {
    'risk_0001': 'roadmap_stage_0003',   # 관심군    → 역량 준비
    'risk_0002': 'roadmap_stage_0002',   # 고립위험군 → 탐색 시작
    'risk_0003': 'roadmap_stage_0002',   # 고립군    → 탐색 시작
    'risk_0004': 'roadmap_stage_0001',   # 은둔위험군 → 상태 인식
    'risk_0005': 'roadmap_stage_0001',   # 은둔군    → 상태 인식
}

rows_rtr, idx = [], 1
for risk_id, roadmap_id in RISK_TO_ROADMAP.items():
    rows_rtr.append({'relation_id': f'rtr_{idx:05d}', 'risk_stage_id': risk_id,
                      'roadmap_stage_id': roadmap_id, 'is_active': 'True'})
    idx += 1

out = os.path.join(RELATIONS, 'risk_stage_to_roadmap_stage.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['relation_id','risk_stage_id','roadmap_stage_id','is_active'])
    w.writeheader(); w.writerows(rows_rtr)
print(f'[risk->roadmap]    {len(rows_rtr)}행')

# ── 5. risk_stage_to_domain.csv ─────────────────────────────
# 접근성 티어: 1=진입장벽 낮음, 4=높음
DOMAIN_TIER = {
    'domain_0030': 1, 'domain_0031': 1, 'domain_0024': 1, 'domain_0038': 1,
    'domain_0026': 1, 'domain_0027': 1, 'domain_0025': 1, 'domain_0032': 1,
    'domain_0002': 1, 'domain_0033': 1,
    'domain_0001': 2, 'domain_0006': 2, 'domain_0010': 2, 'domain_0012': 2,
    'domain_0013': 2, 'domain_0017': 2, 'domain_0018': 2, 'domain_0019': 2,
    'domain_0029': 2, 'domain_0034': 2, 'domain_0035': 2,
    'domain_0003': 3, 'domain_0005': 3, 'domain_0007': 3, 'domain_0008': 3,
    'domain_0011': 3, 'domain_0014': 3, 'domain_0015': 3, 'domain_0016': 3,
    'domain_0020': 3, 'domain_0023': 3, 'domain_0028': 3, 'domain_0036': 3,
    'domain_0037': 3,
    'domain_0004': 4, 'domain_0009': 4, 'domain_0021': 4, 'domain_0022': 4,
    'domain_0039': 4, 'domain_0040': 4, 'domain_0041': 4, 'domain_0042': 4,
    'domain_0043': 4,
}
# 티어 내 세부 순서 (career value/빈도 기반)
TIER_SUB = {
    'domain_0030': 1, 'domain_0031': 2, 'domain_0024': 3, 'domain_0038': 4,
    'domain_0026': 5, 'domain_0027': 6, 'domain_0025': 7, 'domain_0032': 8,
    'domain_0002': 9, 'domain_0033':10,
    'domain_0001': 1, 'domain_0006': 2, 'domain_0010': 3, 'domain_0012': 4,
    'domain_0013': 5, 'domain_0017': 6, 'domain_0018': 7, 'domain_0019': 8,
    'domain_0029': 9, 'domain_0034':10, 'domain_0035':11,
    'domain_0003': 1, 'domain_0005': 2, 'domain_0007': 3, 'domain_0008': 4,
    'domain_0011': 5, 'domain_0014': 6, 'domain_0015': 7, 'domain_0016': 8,
    'domain_0020': 9, 'domain_0023':10, 'domain_0028':11, 'domain_0036':12,
    'domain_0037':13,
    'domain_0004': 1, 'domain_0009': 2, 'domain_0021': 3, 'domain_0022': 4,
    'domain_0039': 5, 'domain_0040': 6, 'domain_0041': 7, 'domain_0042': 8,
    'domain_0043': 9,
}
# risk별 tier 우선순위 (낮은 숫자 = 먼저 추천)
RISK_TIER_PRIO = {
    'risk_0001': {1:3, 2:1, 3:2, 4:4},   # 관심군: career-value(tier2) 우선
    'risk_0002': {1:2, 2:1, 3:3, 4:4},   # 고립위험군: 균형
    'risk_0003': {1:1, 2:2, 3:3, 4:4},   # 고립군: 접근성 우선
    'risk_0004': {1:1, 2:2, 3:3, 4:4},   # 은둔위험군: 접근성 강
    'risk_0005': {1:1, 2:2, 3:3, 4:4},   # 은둔군: 접근성 최우선
}

rows_rtd, idx = [], 1
for risk in sorted(risks, key=lambda x: x['risk_stage_id']):
    risk_id = risk['risk_stage_id']
    prio = RISK_TIER_PRIO[risk_id]
    sorted_domains = sorted(
        domain_ids,
        key=lambda d: (prio[DOMAIN_TIER[d]], TIER_SUB.get(d, 99))
    )
    for rank, domain_id in enumerate(sorted_domains, start=1):
        rows_rtd.append({
            'relation_id':         f'rtd_{idx:05d}',
            'risk_stage_id':       risk_id,
            'domain_sub_label_id': domain_id,
            'priority_rank':       rank,
            'is_active':           'True',
        })
        idx += 1

out = os.path.join(RELATIONS, 'risk_stage_to_domain.csv')
with open(out, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['relation_id','risk_stage_id','domain_sub_label_id','priority_rank','is_active'])
    w.writeheader(); w.writerows(rows_rtd)
print(f'[risk->domain]     {len(rows_rtd)}행  ({len(risks)}risk x {len(domain_ids)}domain)')

print()
print('=== 완료 ===')
print(f'relations/ 파일 목록:')
for f in sorted(os.listdir(RELATIONS)):
    if f.endswith('.csv'):
        cnt = sum(1 for _ in open(os.path.join(RELATIONS, f), encoding='utf-8')) - 1
        print(f'  {f}: {cnt:,}행')
