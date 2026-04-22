import React, { useState, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Search, Map, ExternalLink } from 'lucide-react';
import certCandidatesData from '../../data/cert_candidates.json';

const Recommendation: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // 실 구현에서는 location.state 에서 넘어온 정보를 기반으로 API를 호출합니다.
  const riskStageId = location.state?.riskStageId || '선택안함';

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('');

  const riskStageMapping: Record<string, string> = {
    'risk_stage_1': 'risk_0001',
    'risk_stage_2': 'risk_0002',
    'risk_stage_3': 'risk_0003',
    'risk_stage_4': 'risk_0004',
    'risk_stage_5': 'risk_0005',
    '선택안함': ''
  };
  const targetRiskStage = riskStageMapping[riskStageId] || '';

  // 필터링 로직 구현 (실제 마스터 데이터셋 연동)
  const filteredCandidates = useMemo(() => {
    return certCandidatesData.filter((cert: any) => {
      // 1. 위험군 필터링 (location.state를 통해 넘어온 진단 결과 적용)
      if (targetRiskStage && (!cert.recommended_risk_stages || !cert.recommended_risk_stages.includes(targetRiskStage))) {
        return false;
      }
      
      const searchTarget = cert.text_for_dense || '';
      
      // 2. 검색어 필터링
      const matchQuery = !searchQuery || cert.cert_name.includes(searchQuery) || searchTarget.includes(searchQuery);
      
      // 3. 관심 직무 필터링
      const matchJob = selectedJob === "" || searchTarget.includes(selectedJob);
      
      // 4. 관심 도메인 필터링
      const matchDomain = selectedDomain === "" || searchTarget.includes(selectedDomain);

      return matchQuery && matchJob && matchDomain;
    });
  }, [searchQuery, selectedJob, selectedDomain, targetRiskStage]);

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
              <option value="데이터">데이터 관련</option>
              <option value="개발">개발 (소프트웨어/웹/앱)</option>
              <option value="기계">기계/생산/제조</option>
              <option value="전기">전기/전자/통신</option>
              <option value="설계">설계/건축/토목</option>
              <option value="기획">경영/기획/사무</option>
            </select>
          </div>
          <div className="filter-group">
            <label>관심 도메인</label>
            <select value={selectedDomain} onChange={(e) => setSelectedDomain(e.target.value)} className="filter-select">
              <option value="">전체 도메인</option>
              <option value="IT">IT/소프트웨어</option>
              <option value="기계">기계/제조</option>
              <option value="전기">전기/전자</option>
              <option value="건축">건축/토목</option>
              <option value="디자인">디자인/예술</option>
            </select>
          </div>
          <button className="btn-primary" style={{ alignSelf: 'flex-end', height: '42px' }}>
            검색
          </button>
        </div>
      </div>

      <div className="results-section">
        <h2 className="section-title">추천 후보 ({filteredCandidates.length})</h2>
        <div className="candidates-grid">
          {filteredCandidates.slice(0, 50).map((cert: any) => (
            <div key={cert.candidate_id} className="glass-card cert-card">
              <div className="cert-header">
                <div>
                  <span className="domain-badge">{cert.cert_grade_tier || '등급 미상'}</span>
                  <h3 className="cert-title">{cert.cert_name}</h3>
                </div>
              </div>
              <p className="cert-summary" style={{ fontSize: '0.85rem' }}>{cert.text_for_dense}</p>
              
              <div className="cert-tags">
                <div className="tag-group">
                  <span className="tag-label">추천 위험군 단계:</span>
                  {(cert.recommended_risk_stages || []).map((risk: string) => <span key={risk} className="tag">{risk}</span>)}
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
