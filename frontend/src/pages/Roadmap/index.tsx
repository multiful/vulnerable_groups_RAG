import React from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle2, Circle, Clock, ArrowLeft } from 'lucide-react';

const RISK_STAGE_LABELS: Record<string, string> = {
  '1': '1단계',
  '2': '2단계',
  '3': '3단계',
  '4': '4단계',
  '5': '5단계',
};

// Stub data based on API_SPEC.md examples
const MOCK_STAGES = [
  {
    id: 'roadmap_stage_01',
    name: '기초',
    desc: '기본 개념과 직무 연관성을 이해하는 단계입니다.',
    certIds: ['cert_013'],
    status: 'completed' as const,
  },
  {
    id: 'roadmap_stage_02',
    name: '실무',
    desc: '실무 적용 가능성을 높이는 단계입니다.',
    certIds: ['cert_013'],
    status: 'current' as const,
  },
  {
    id: 'roadmap_stage_03',
    name: '심화',
    desc: '직무 전문성을 입증할 수 있는 고급 자격증 취득 단계입니다.',
    certIds: ['cert_099'],
    status: 'locked' as const,
  },
];

type StageStatus = 'completed' | 'current' | 'locked';

function StageIcon({ status }: { status: StageStatus }) {
  if (status === 'completed') return <CheckCircle2 size={22} className="icon-success" />;
  if (status === 'current') return <Clock size={22} className="icon-secondary" />;
  return <Circle size={22} className="icon-muted" />;
}

const Roadmap: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const certId = searchParams.get('cert') ?? 'cert_013';
  const stageParam = searchParams.get('stage') ?? '';
  const riskLabel = stageParam ? (RISK_STAGE_LABELS[stageParam] ?? stageParam) : '';

  return (
    <div className="roadmap-wrap">
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate(-1)}>
          <ArrowLeft size={16} /> 뒤로
        </button>
        <h1 className="page-title">성장 로드맵</h1>
        <p className="page-desc">
          목표 자격증{riskLabel ? ` · ${riskLabel}` : ''} 기준 단계별 학습 경로입니다.
        </p>
      </div>

      <div className="card roadmap-card">
        <div className="timeline">
          {MOCK_STAGES.map((stage, idx) => (
            <div key={stage.id} className={`tl-row ${stage.status}`}>
              {/* Left: connector */}
              <div className="tl-left">
                <StageIcon status={stage.status} />
                {idx < MOCK_STAGES.length - 1 && (
                  <div className={`tl-line ${stage.status === 'completed' ? 'done' : ''}`} />
                )}
              </div>

              {/* Right: content */}
              <div className="tl-content">
                <div className="tl-header">
                  <span className={`badge tl-badge ${stage.status === 'current' ? 'badge-secondary' : stage.status === 'completed' ? 'badge-success' : 'badge-neutral'}`}>
                    {stage.status === 'completed' ? '완료' : stage.status === 'current' ? '진행중' : '잠김'}
                  </span>
                  <h3 className="tl-name">{stage.name}</h3>
                </div>
                <p className="tl-desc">{stage.desc}</p>
                <div className="tl-certs">
                  {stage.certIds.map(id => (
                    <span key={id} className={`cert-chip ${id === certId ? 'cert-chip-target' : ''}`}>
                      {id === certId ? '★ ' : ''}{id}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <style>{`
        .roadmap-wrap {
          max-width: 680px;
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .back-btn {
          display: inline-flex;
          align-items: center;
          gap: 0.375rem;
          font-size: 0.875rem;
          color: var(--text-muted);
          font-weight: 500;
          margin-bottom: 0.5rem;
          transition: var(--transition);
        }
        .back-btn:hover { color: var(--text); }

        .roadmap-card { padding: 2rem 1.75rem; }
        .timeline { display: flex; flex-direction: column; gap: 0; }

        .tl-row {
          display: flex;
          gap: 1.25rem;
        }
        /* Left column: icon + vertical line */
        .tl-left {
          display: flex;
          flex-direction: column;
          align-items: center;
          flex-shrink: 0;
          width: 22px;
        }
        .tl-line {
          flex: 1;
          width: 2px;
          background: var(--border);
          margin: 4px 0;
          min-height: 32px;
        }
        .tl-line.done {
          background: linear-gradient(180deg, var(--success), var(--primary));
        }

        /* Right column: content */
        .tl-content {
          flex: 1;
          padding-bottom: 2rem;
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .tl-row:last-child .tl-content { padding-bottom: 0; }

        .tl-header {
          display: flex;
          align-items: center;
          gap: 0.625rem;
        }
        .tl-name { font-size: 1.05rem; font-weight: 700; color: var(--text); }
        .tl-row.locked .tl-name { color: var(--text-muted); }

        .tl-desc { font-size: 0.875rem; color: var(--text-muted); line-height: 1.6; }
        .tl-certs {
          display: flex;
          flex-wrap: wrap;
          gap: 0.375rem;
          margin-top: 0.25rem;
        }
        .cert-chip {
          padding: 0.2rem 0.6rem;
          border-radius: var(--radius-xs);
          border: 1px solid var(--border);
          font-size: 0.78rem;
          color: var(--text-muted);
          background: var(--surface-2);
        }
        .cert-chip-target {
          border-color: var(--primary);
          color: var(--primary);
          background: var(--primary-light);
          font-weight: 600;
        }

        /* Icon colors */
        .icon-success { color: var(--success); }
        .icon-secondary { color: var(--secondary); }
        .icon-muted { color: var(--text-light); }
      `}</style>
    </div>
  );
};

export default Roadmap;
