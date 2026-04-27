import React, { useState, useMemo, useDeferredValue } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Search, Map, ExternalLink, ChevronDown, AlertCircle } from 'lucide-react';
import certCandidatesData from '../../data/cert_candidates.json';
import type { CertCandidate } from '../../types/cert';

const certs = certCandidatesData as CertCandidate[];

const RISK_STAGE_LABELS: Record<string, string> = {
  '1': '1단계',
  '2': '2단계',
  '3': '3단계',
  '4': '4단계',
  '5': '5단계',
};

const RISK_INTERNAL_MAP: Record<string, string> = {
  '1': 'risk_0001',
  '2': 'risk_0002',
  '3': 'risk_0003',
  '4': 'risk_0004',
  '5': 'risk_0005',
};

function gradeBadgeClass(tier: string): string {
  if (tier.startsWith('5')) return 'badge-primary';
  if (tier.startsWith('4')) return 'badge-primary';
  if (tier.startsWith('3')) return 'badge-secondary';
  if (tier.startsWith('2')) return 'badge-success';
  if (tier.startsWith('1')) return 'badge-warning';
  return 'badge-neutral';
}

function gradeLabel(tier: string): string {
  const map: Record<string, string> = {
    '5_기능장': '기능장',
    '4_기술사': '기술사',
    '3_기사': '기사',
    '2_산업기사': '산업기사',
    '1_기능사': '기능사',
  };
  return map[tier] ?? (tier || '기타');
}

const Recommendation: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const stageParam = searchParams.get('stage') ?? '';

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');

  const deferredQuery = useDeferredValue(searchQuery);

  const targetRiskInternal = stageParam ? RISK_INTERNAL_MAP[stageParam] : '';
  const riskLabel = stageParam ? (RISK_STAGE_LABELS[stageParam] ?? stageParam) : '';

  const filtered = useMemo(() => {
    return certs.filter(cert => {
      if (targetRiskInternal && !cert.recommended_risk_stages.includes(targetRiskInternal)) return false;
      const haystack = cert.text_for_dense;
      if (deferredQuery && !cert.cert_name.includes(deferredQuery) && !haystack.includes(deferredQuery)) return false;
      if (selectedJob && !haystack.includes(selectedJob)) return false;
      if (selectedDomain && !haystack.includes(selectedDomain)) return false;
      return true;
    });
  }, [deferredQuery, selectedJob, selectedDomain, targetRiskInternal]);

  const handleRoadmap = (certId: string) => {
    const params = new URLSearchParams();
    params.set('cert', certId);
    if (stageParam) params.set('stage', stageParam);
    navigate(`/roadmap?${params.toString()}`);
  };

  return (
    <div className="rec-wrap">
      <div className="page-header">
        <h1 className="page-title">자격증 추천</h1>
        <p className="page-desc">
          {riskLabel
            ? `${riskLabel} 기준으로 적합한 자격증을 보여드립니다.`
            : '관심 직무와 도메인으로 자격증을 탐색하세요.'}
        </p>
      </div>

      {/* No risk stage selected — prompt */}
      {!stageParam && (
        <div className="empty-hint card">
          <AlertCircle size={20} />
          <div>
            <p className="empty-hint-title">위험군 진단을 먼저 해보세요</p>
            <p className="empty-hint-sub">진단 결과를 바탕으로 더 정확한 추천을 드릴 수 있습니다.</p>
          </div>
          <button className="btn-ghost" onClick={() => navigate('/risk-assessment')}>
            진단하러 가기
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="card filter-card">
        <div className="search-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="input search-input"
            placeholder="자격증명, 직무, 도메인으로 검색…"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="filter-row">
          <div className="filter-group">
            <label className="filter-label">관심 직무</label>
            <div className="select-wrap">
              <select
                className="select"
                value={selectedJob}
                onChange={e => setSelectedJob(e.target.value)}
              >
                <option value="">전체 직무</option>
                <option value="데이터">데이터 관련</option>
                <option value="개발">개발 (소프트웨어/웹/앱)</option>
                <option value="기계">기계/생산/제조</option>
                <option value="전기">전기/전자/통신</option>
                <option value="설계">설계/건축/토목</option>
                <option value="기획">경영/기획/사무</option>
              </select>
              <ChevronDown size={16} className="select-arrow" />
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">관심 도메인</label>
            <div className="select-wrap">
              <select
                className="select"
                value={selectedDomain}
                onChange={e => setSelectedDomain(e.target.value)}
              >
                <option value="">전체 도메인</option>
                <option value="IT">IT/소프트웨어</option>
                <option value="기계">기계/제조</option>
                <option value="전기">전기/전자</option>
                <option value="건축">건축/토목</option>
                <option value="디자인">디자인/예술</option>
              </select>
              <ChevronDown size={16} className="select-arrow" />
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      <section>
        <p className="section-title result-count">
          추천 자격증 <span className="count-num">{filtered.length}</span>건
        </p>
        <div className="cert-grid">
          {filtered.slice(0, 50).map(cert => (
            <div key={cert.candidate_id} className="card cert-card">
              <div className="cert-top">
                <span className={`badge ${gradeBadgeClass(cert.cert_grade_tier)}`}>
                  {gradeLabel(cert.cert_grade_tier)}
                </span>
                <h3 className="cert-name">{cert.cert_name}</h3>
                <p className="cert-issuer">{cert.issuer}</p>
              </div>

              <p className="cert-summary">{cert.text_for_dense}</p>

              <div className="cert-stages">
                {cert.recommended_risk_stages.map(rs => {
                  const stageNum = rs.replace('risk_000', '');
                  return (
                    <span key={rs} className="badge badge-neutral">
                      {stageNum}단계
                    </span>
                  );
                })}
              </div>

              <div className="cert-actions">
                <button className="text-btn">
                  <ExternalLink size={14} /> 설명 근거
                </button>
                <button
                  className="text-btn roadmap-btn"
                  onClick={() => handleRoadmap(cert.cert_id)}
                >
                  <Map size={14} /> 로드맵 보기
                </button>
              </div>
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="no-results">
              <p>조건에 맞는 자격증이 없습니다.</p>
              <p>검색어나 필터를 변경해보세요.</p>
            </div>
          )}
        </div>
      </section>

      <style>{`
        .rec-wrap {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        /* Empty hint */
        .empty-hint {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem 1.25rem;
          color: var(--text-muted);
          flex-wrap: wrap;
        }
        .empty-hint-title { font-weight: 600; color: var(--text); font-size: 0.9rem; }
        .empty-hint-sub { font-size: 0.825rem; color: var(--text-muted); }
        .empty-hint > div { flex: 1; min-width: 180px; }

        /* Filter card */
        .filter-card {
          padding: 1.25rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .filter-row {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 0.375rem;
          flex: 1;
          min-width: 180px;
        }
        .filter-label {
          font-size: 0.8rem;
          font-weight: 600;
          color: var(--text-muted);
        }
        .select-wrap {
          position: relative;
          display: flex;
          align-items: center;
        }
        .select-arrow {
          position: absolute;
          right: 0.75rem;
          color: var(--text-light);
          pointer-events: none;
        }

        /* Results */
        .result-count {
          margin-bottom: 1rem;
        }
        .count-num {
          color: var(--primary);
          font-size: 1.25rem;
          font-weight: 800;
        }
        .cert-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }
        .cert-card {
          padding: 1.25rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          transition: box-shadow 0.22s ease, border-color 0.22s ease, transform 0.22s ease;
        }
        .cert-card:hover {
          box-shadow: 0 8px 28px rgba(99,102,241,0.14), var(--shadow-md);
          border-color: rgba(99,102,241,0.2);
          transform: translateY(-3px);
        }

        .cert-top { display: flex; flex-direction: column; gap: 0.25rem; }
        .cert-name { font-size: 1.05rem; font-weight: 700; color: var(--text); }
        .cert-issuer { font-size: 0.78rem; color: var(--text-light); }

        .cert-summary {
          font-size: 0.825rem;
          color: var(--text-muted);
          line-height: 1.55;
          display: -webkit-box;
          -webkit-line-clamp: 3;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        .cert-stages {
          display: flex;
          flex-wrap: wrap;
          gap: 0.375rem;
        }
        .cert-actions {
          display: flex;
          gap: 1rem;
          padding-top: 0.75rem;
          border-top: 1px solid var(--border);
          margin-top: auto;
        }
        .roadmap-btn { margin-left: auto; }

        /* Empty state */
        .no-results {
          grid-column: 1 / -1;
          text-align: center;
          padding: 3rem 1rem;
          color: var(--text-muted);
          line-height: 1.8;
        }
      `}</style>
    </div>
  );
};

export default Recommendation;
