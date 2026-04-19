import sys, os, csv, json
sys.path.insert(0, '.')
from backend.app.services import recommendation_service as rs

with open('data/processed/master/domain_master.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        if r['domain_sub_label_id'] == 'domain_0005':
            print('domain_0005 =', r.get('domain_sub_label_name'), '|parent=', r.get('parent_label_name', '-'))
            break

res = rs.recommendations({
    'risk_stage_id': 'risk_0005',
    'domain_ids': ['domain_0005'],
    'top_n_per_stage': 5,
})
d = res['data']
print('total_certs=', d['total_certs_in_roadmap'], 'fallback=', d['fallback_used'])
print('entry_advanced=', d['entry_advanced'])

os.makedirs('tmp_inspect', exist_ok=True)
arrow = ' -> '
with open('tmp_inspect/golden_risk5_domain5.txt', 'w', encoding='utf-8') as out:
    rs_info = d.get('risk_stage') or {}
    st = d.get('starting_roadmap_stage') or {}
    out.write(f'=== risk_0005 + domain_0005 ({rs_info.get("name", "")}) ===\n')
    out.write(f'starting_stage = {st.get("name", "")} (order={st.get("order")})\n\n')
    out.write('== roadmap_by_stage ==\n')
    for stage in d['roadmap_by_stage']:
        s = stage['stage']
        certs = stage['recommended_certs']
        out.write(f'\n-- {s["name"]} (order={s["order"]}) -- {len(certs)}개\n')
        for c in certs:
            out.write(f'  [{c["cert_grade_tier"]:<8}] {c["cert_name"]:<22} pass={c["avg_pass_rate"]}% bottleneck={c["is_bottleneck"]} {c["achievability"]}\n')
    out.write('\n== roadmap_sequence (flat top 15) ==\n')
    for s in d['roadmap_sequence'][:15]:
        out.write(f'  step {s["step"]:>2}: [{s["cert_grade_tier"]:<8}] {s["cert_name"]:<22} stage={s["roadmap_stage_id"]} pass={s["avg_pass_rate"]}%\n')
    out.write('\n== cert_paths top 5 ==\n')
    for p in d['cert_paths']:
        names = [s['cert_name'] for s in p['steps']]
        out.write(f'  score={p["path_score"]:.3f} len={p["length"]}: {arrow.join(names)}\n')
print('dumped tmp_inspect/golden_risk5_domain5.txt')
