import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Info } from 'lucide-react';

const RiskAssessment: React.FC = () => {
  const navigate = useNavigate();
  const [selectedStage, setSelectedStage] = useState<string>('');

  const riskStages = [
    { id: '1', title: '1단계: 안정/초기', desc: '기본적인 준비가 되어 있으며, 명확한 목표 설정이 필요한 단계' },
    { id: '2', title: '2단계: 탐색/준비', desc: '관심 분야를 탐색하고 있으며, 구체적인 방향성을 찾고 있는 단계' },
    { id: '3', title: '3단계: 정체/고민', desc: '취업 준비 기간이 길어지거나 방향성에 대해 고민이 많은 단계' },
    { id: '4', title: '4단계: 취약/집중 케어', desc: '실질적인 기초 역량 강화와 작은 성공 경험이 우선적으로 필요한 단계' },
    { id: '5', title: '5단계: 고위험/기초', desc: '심리적 안정과 아주 기본적인 직무 탐색부터 천천히 시작해야 하는 단계' }
  ];

  const handleNext = () => {
    // 실 서비스에서는 상태 관리나 API 호출을 통해 다음 페이지로 데이터 전달
    if (selectedStage) {
      navigate('/recommendation', { state: { riskStageId: `risk_stage_${selectedStage}` } });
    }
  };

  return (
    <div className="risk-container">
      <div className="page-header">
        <h1 className="page-title">위험군 진단</h1>
        <p className="page-desc">현재 상황에 가장 가까운 단계를 선택해주세요.</p>
      </div>

      <div className="glass-card assessment-content">
        <div className="info-box">
          <Info size={20} color="var(--secondary)" />
          <span>선택한 단계에 따라 추천되는 자격증의 권장 등급(난이도)이 조정됩니다.</span>
        </div>

        <div className="stages-list">
          {riskStages.map((stage) => (
            <div 
              key={stage.id}
              className={`stage-option ${selectedStage === stage.id ? 'selected' : ''}`}
              onClick={() => setSelectedStage(stage.id)}
            >
              <div className="stage-radio">
                <div className="radio-inner" />
              </div>
              <div className="stage-info">
                <h3>{stage.title}</h3>
                <p>{stage.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="actions">
          <button 
            className="btn-primary" 
            disabled={!selectedStage}
            onClick={handleNext}
            style={{ opacity: selectedStage ? 1 : 0.5, pointerEvents: selectedStage ? 'auto' : 'none' }}
          >
            다음 단계로 <ArrowRight size={20} />
          </button>
        </div>
      </div>

      <style>{`
        .risk-container {
          max-width: 800px;
          margin: 0 auto;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }
        .page-header {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .page-title {
          font-size: 2rem;
          font-weight: 700;
        }
        .page-desc {
          color: var(--text-muted);
          font-size: 1.1rem;
        }
        .assessment-content {
          padding: 2rem;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }
        .info-box {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem;
          background: rgba(6, 182, 212, 0.1);
          border: 1px solid rgba(6, 182, 212, 0.2);
          border-radius: 0.75rem;
          color: var(--secondary);
          font-size: 0.95rem;
        }
        .stages-list {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .stage-option {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          padding: 1.5rem;
          border-radius: 1rem;
          border: 1px solid var(--border);
          background: rgba(30, 41, 59, 0.4);
          cursor: pointer;
          transition: var(--transition);
        }
        .stage-option:hover {
          border-color: var(--text-muted);
          background: rgba(30, 41, 59, 0.8);
        }
        .stage-option.selected {
          border-color: var(--primary);
          background: rgba(99, 102, 241, 0.1);
        }
        .stage-radio {
          width: 1.25rem;
          height: 1.25rem;
          border-radius: 50%;
          border: 2px solid var(--text-muted);
          margin-top: 0.25rem;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: var(--transition);
        }
        .stage-option.selected .stage-radio {
          border-color: var(--primary);
        }
        .radio-inner {
          width: 0.625rem;
          height: 0.625rem;
          border-radius: 50%;
          background: var(--primary);
          transform: scale(0);
          transition: var(--transition);
        }
        .stage-option.selected .radio-inner {
          transform: scale(1);
        }
        .stage-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .stage-info h3 {
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--text);
        }
        .stage-info p {
          color: var(--text-muted);
          font-size: 0.95rem;
        }
        .actions {
          display: flex;
          justify-content: flex-end;
          margin-top: 1rem;
        }
      `}</style>
    </div>
  );
};

export default RiskAssessment;
