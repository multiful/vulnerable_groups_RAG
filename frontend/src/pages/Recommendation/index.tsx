import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Map, ExternalLink } from 'lucide-react';

const Recommendation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // 실 구현에서는 location.state 에서 넘어온 정보를 기반으로 API를 호출합니다.
  const riskStageId = location.state?.riskStageId || '선택안함';

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');

  // 스텁(Mock) 데이터 (API_SPEC.md 참고)
  const mockCandidates = [
    {
      candidate_id: "cand_cert_013",
      cert_id: "cert_013",
      cert_name: "정보처리기사",
      primary_domain: "데이터/AI",
      related_jobs: ["데이터 분석", "백엔드 개발"],
      related_domains: ["데이터/AI", "소프트웨어개발"],
      roadmap_stages: ["기초", "실무"],
      summary: "데이터/AI 및 소프트웨어개발 영역으로 연결되는 대표 자격증입니다."
    },
    {
      candidate_id: "cand_cert_014",
      cert_id: "cert_014",
      cert_name: "웹디자인기능사",
      primary_domain: "소프트웨어개발",
      related_jobs: ["프론트엔드 개발", "UX/UI 디자이너"],
      related_domains: ["소프트웨어개발", "디자인"],
      roadmap_stages: ["탐색", "기초"],
      summary: "UI 구현 및 웹 퍼블리싱의 기초를 다질 수 있는 자격증입니다. 4~5단계 위험군에게 우선 추천됩니다."
    }
  ];

  const handleCreateRoadmap = (certId: string) => {
    navigate('/roadmap', { state: { certId, riskStageId } });
  };

  return (
    <div className="recommendation-container">
      <div className="page-header">
        <h1 className="page-title">자격증 추천</h1>
        <p className="page-desc">관심 직무와 도메인을 검색하여 맞춤형 자격증을 확인하세요. (현재 진단: {riskStageId})</p>
      </div>

      <div className="glass-card filter-section">
        <div className="search-box">
          <Search size={20} className="search-icon" />
          <input 
            type="text" 
            placeholder="자유롭게 입력해보세요 (예: 데이터 분석 쪽으로 갈 때 도움이 되는 자격증)" 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
        
        <div className="filter-row">
          <div className="filter-group">
            <label>관심 직무</label>
            <select value={selectedJob} onChange={(e) => setSelectedJob(e.target.value)} className="filter-select">
              <option value="">전체 직무</option>
              <option value="데이터 분석">데이터 분석</option>
              <option value="백엔드 개발">백엔드 개발</option>
              <option value="프론트엔드 개발">프론트엔드 개발</option>
            </select>
          </div>
          <div className="filter-group">
            <label>관심 도메인</label>
            <select value={selectedDomain} onChange={(e) => setSelectedDomain(e.target.value)} className="filter-select">
              <option value="">전체 도메인</option>
              <option value="데이터/AI">데이터/AI</option>
              <option value="소프트웨어개발">소프트웨어개발</option>
              <option value="디자인">디자인</option>
            </select>
          </div>
          <button className="btn-primary" style={{ alignSelf: 'flex-end', height: '42px' }}>
            검색
          </button>
        </div>
      </div>

      <div className="results-section">
        <h2 className="section-title">추천 후보 ({mockCandidates.length})</h2>
        <div className="candidates-grid">
          {mockCandidates.map((cert) => (
            <div key={cert.candidate_id} className="glass-card cert-card">
              <div className="cert-header">
                <div>
                  <span className="domain-badge">{cert.primary_domain}</span>
                  <h3 className="cert-title">{cert.cert_name}</h3>
                </div>
              </div>
              <p className="cert-summary">{cert.summary}</p>
              
              <div className="cert-tags">
                <div className="tag-group">
                  <span className="tag-label">관련 직무:</span>
                  {cert.related_jobs.map(job => <span key={job} className="tag">{job}</span>)}
                </div>
              </div>

              <div className="cert-actions">
                <button className="action-btn text-blue">
                  <ExternalLink size={16} /> 설명 근거 (문서)
                </button>
                <button 
                  className="action-btn text-primary"
                  onClick={() => handleCreateRoadmap(cert.cert_id)}
                >
                  <Map size={16} /> 로드맵 생성
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .recommendation-container {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }
        .page-header {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .page-title { font-size: 2rem; font-weight: 700; }
        .page-desc { color: var(--text-muted); font-size: 1.1rem; }
        
        .filter-section {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .search-box {
          position: relative;
          display: flex;
          align-items: center;
        }
        .search-icon {
          position: absolute;
          left: 1rem;
          color: var(--text-muted);
        }
        .search-input {
          width: 100%;
          padding: 1rem 1rem 1rem 3rem;
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--border);
          border-radius: 0.75rem;
          color: var(--text);
          font-size: 1rem;
          outline: none;
          transition: var(--transition);
        }
        .search-input:focus { border-color: var(--primary); }
        
        .filter-row {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          flex: 1;
          min-width: 200px;
        }
        .filter-group label {
          font-size: 0.875rem;
          color: var(--text-muted);
          font-weight: 500;
        }
        .filter-select {
          padding: 0.75rem 1rem;
          background: rgba(15, 23, 42, 0.5);
          border: 1px solid var(--border);
          border-radius: 0.5rem;
          color: var(--text);
          outline: none;
          appearance: none;
        }
        
        .results-section {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .section-title { font-size: 1.25rem; font-weight: 600; }
        .candidates-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
          gap: 1.5rem;
        }
        .cert-card {
          padding: 1.5rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .cert-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }
        .domain-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          background: rgba(99, 102, 241, 0.1);
          color: var(--primary);
          border-radius: 1rem;
          font-size: 0.75rem;
          font-weight: 600;
          margin-bottom: 0.75rem;
        }
        .cert-title {
          font-size: 1.25rem;
          font-weight: 700;
        }
        .cert-summary {
          color: var(--text-muted);
          font-size: 0.95rem;
          line-height: 1.5;
        }
        .cert-tags {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-top: 0.5rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border);
        }
        .tag-group {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          flex-wrap: wrap;
        }
        .tag-label {
          font-size: 0.85rem;
          color: var(--text-muted);
        }
        .tag {
          background: var(--surface);
          padding: 0.2rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.8rem;
          color: var(--text);
        }
        .cert-actions {
          display: flex;
          gap: 1rem;
          margin-top: auto;
          padding-top: 1rem;
        }
        .action-btn {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.9rem;
          font-weight: 500;
          transition: var(--transition);
        }
        .action-btn:hover { text-decoration: underline; }
        .text-blue { color: #3b82f6; }
        .text-primary { color: var(--primary); }
      `}</style>
    </div>
  );
};

export default Recommendation;
