import React from 'react';
import { useLocation } from 'react-router-dom';
import { CheckCircle2, Circle, Clock } from 'lucide-react';

const Roadmap: React.FC = () => {
  const location = useLocation();
  const certId = location.state?.certId || 'cert_013';
  
  // API_SPEC.md 예시 데이터 기반 스텁
  const mockRoadmap = [
    {
      roadmap_stage_id: "roadmap_stage_01",
      roadmap_stage_name: "기초",
      description: "기본 개념과 직무 연관성을 이해하는 단계입니다.",
      related_cert_ids: ["cert_013"],
      status: "completed" // UI 표시용 가상 속성
    },
    {
      roadmap_stage_id: "roadmap_stage_02",
      roadmap_stage_name: "실무",
      description: "실무 적용 가능성을 높이는 단계입니다.",
      related_cert_ids: ["cert_013"],
      status: "current"
    },
    {
      roadmap_stage_id: "roadmap_stage_03",
      roadmap_stage_name: "심화",
      description: "직무 전문성을 입증할 수 있는 고급 자격증 취득 단계입니다.",
      related_cert_ids: ["cert_099"],
      status: "locked"
    }
  ];

  return (
    <div className="roadmap-container">
      <div className="page-header">
        <h1 className="page-title">성장 로드맵</h1>
        <p className="page-desc">추천된 자격증 취득을 위한 단계별 경로입니다. (현재 목표: {certId})</p>
      </div>

      <div className="glass-card roadmap-content">
        <div className="timeline">
          {mockRoadmap.map((stage, index) => (
            <div key={stage.roadmap_stage_id} className={`timeline-item ${stage.status}`}>
              <div className="timeline-connector">
                {index !== mockRoadmap.length - 1 && <div className="line" />}
                <div className="node">
                  {stage.status === 'completed' ? <CheckCircle2 size={24} color="var(--primary)" /> : 
                   stage.status === 'current' ? <Clock size={24} color="var(--secondary)" /> : 
                   <Circle size={24} color="var(--text-muted)" />}
                </div>
              </div>
              
              <div className="timeline-content">
                <div className="stage-header">
                  <span className="stage-badge">해금 단계 {index + 1}</span>
                  <h3>{stage.roadmap_stage_name}</h3>
                </div>
                <p className="stage-desc">{stage.description}</p>
                <div className="cert-list">
                  <span>추천 목표: </span>
                  {stage.related_cert_ids.map(id => (
                    <span key={id} className="cert-id-badge">{id === certId ? `★ ${id}` : id}</span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .roadmap-container {
          max-width: 800px;
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
        
        .roadmap-content {
          padding: 3rem 2rem;
        }
        .timeline {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }
        .timeline-item {
          display: flex;
          gap: 2rem;
          min-height: 120px;
        }
        .timeline-connector {
          position: relative;
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .line {
          position: absolute;
          top: 24px;
          bottom: -2rem;
          width: 2px;
          background: var(--border);
          z-index: 0;
        }
        .timeline-item.completed .line {
          background: var(--primary);
        }
        .node {
          position: relative;
          z-index: 1;
          background: var(--glass);
          border-radius: 50%;
        }
        
        .timeline-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          padding-bottom: 2rem;
        }
        .stage-header {
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        .stage-badge {
          font-size: 0.75rem;
          font-weight: 600;
          padding: 0.25rem 0.5rem;
          background: var(--surface-hover);
          border-radius: 0.25rem;
          color: var(--text-muted);
        }
        .timeline-item.current .stage-badge {
          background: rgba(6, 182, 212, 0.15);
          color: var(--secondary);
        }
        .timeline-item.completed h3 { color: var(--primary); }
        .timeline-item.current h3 { color: var(--secondary); }
        .timeline-item.locked h3 { color: var(--text-muted); }
        
        .stage-desc {
          color: var(--text-muted);
          line-height: 1.5;
        }
        
        .cert-list {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-top: 0.5rem;
          font-size: 0.9rem;
          color: var(--text-muted);
        }
        .cert-id-badge {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--border);
          padding: 0.2rem 0.5rem;
          border-radius: 0.25rem;
          color: var(--text);
        }
      `}</style>
    </div>
  );
};

export default Roadmap;
