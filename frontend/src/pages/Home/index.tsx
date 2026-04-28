import React from 'react';
import { ArrowRight, ShieldAlert, Award, Map as MapIcon, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const FEATURES = [
  {
    icon: <ShieldAlert size={26} />,
    title: '위험군 진단',
    desc: '취업 준비 상태를 1~5단계로 진단합니다. 단계별로 추천 우선순위와 로드맵 구조가 달라집니다.',
    colorClass: 'feat-primary',
    glowColor: 'rgba(99,102,241,0.15)',
    path: '/risk-assessment',
  },
  {
    icon: <Award size={26} />,
    title: '맞춤 자격증',
    desc: '위험군 단계와 관심 직무·도메인을 바탕으로 관련 자격증 후보를 추천합니다.',
    colorClass: 'feat-secondary',
    glowColor: 'rgba(14,165,233,0.15)',
    path: '/recommendation',
  },
  {
    icon: <MapIcon size={26} />,
    title: '성장 로드맵',
    desc: '선택한 자격증 기준으로 단계별 학습 경로와 준비 순서를 제안합니다.',
    colorClass: 'feat-accent',
    glowColor: 'rgba(244,63,94,0.12)',
    path: '/roadmap',
  },
];

const FLOW_STEPS = [
  { num: '1', label: '위험군 진단', sub: '현재 단계 선택' },
  { num: '2', label: '자격증 추천', sub: '후보 목록 확인' },
  { num: '3', label: '로드맵 탐색', sub: '학습 경로 확인' },
];

const Home: React.FC = () => {
  return (
    <div className="home-wrap">
      {/* Hero */}
      <section className="hero">
        <div className="hero-orb orb-1" aria-hidden="true" />
        <div className="hero-orb orb-2" aria-hidden="true" />
        <div className="hero-content">
          <div className="hero-badge">
            <TrendingUp size={14} />
            <span>청년 위험군 맞춤 자격증·로드맵 추천</span>
          </div>
          <h1 className="hero-title">
            지금 내 상황에 맞는<br />
            <span className="gradient-text">자격증과 성장 경로</span>
          </h1>
          <p className="hero-sub">
            위험군 단계·관심 직무·도메인을 바탕으로 자격증을 추천하고,<br />
            단계별 로드맵을 제안합니다.
          </p>
          <div className="hero-actions">
            <Link to="/risk-assessment" className="btn-primary hero-btn">
              진단 시작하기 <ArrowRight size={18} />
            </Link>
            <Link to="/recommendation" className="btn-ghost hero-btn">
              자격증 둘러보기
            </Link>
          </div>
        </div>
      </section>

      {/* Flow steps */}
      <section className="flow-section">
        <p className="section-eyebrow">이용 흐름</p>
        <div className="flow-steps">
          {FLOW_STEPS.map((s, idx) => (
            <React.Fragment key={s.num}>
              <div className="flow-step">
                <div className="flow-num">{s.num}</div>
                <div className="flow-text">
                  <span className="flow-label">{s.label}</span>
                  <span className="flow-sub">{s.sub}</span>
                </div>
              </div>
              {idx < FLOW_STEPS.length - 1 && (
                <ArrowRight size={16} className="flow-arrow" />
              )}
            </React.Fragment>
          ))}
        </div>
      </section>

      {/* Features */}
      <section>
        <p className="section-eyebrow">주요 기능</p>
        <div className="features-grid">
          {FEATURES.map(feat => (
            <Link
              to={feat.path}
              key={feat.path}
              className="card feature-card"
              style={{ '--feat-glow': feat.glowColor } as React.CSSProperties}
            >
              <div className={`feat-icon-wrap ${feat.colorClass}`}>
                {feat.icon}
              </div>
              <h3 className="feat-title">{feat.title}</h3>
              <p className="feat-desc">{feat.desc}</p>
              <span className="feat-link">
                바로가기 <ArrowRight size={14} />
              </span>
            </Link>
          ))}
        </div>
      </section>

      <style>{`
        .home-wrap {
          display: flex;
          flex-direction: column;
          gap: 3rem;
        }

        /* Hero */
        .hero {
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.25rem;
          padding: 2.5rem 0 1.5rem;
          position: relative;
          overflow: hidden;
        }
        .hero-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.25rem;
          position: relative;
          z-index: 1;
        }

        /* Orbs */
        .hero-orb {
          position: absolute;
          border-radius: 50%;
          filter: blur(72px);
          pointer-events: none;
          z-index: 0;
        }
        .orb-1 {
          width: 480px; height: 480px;
          background: radial-gradient(circle, rgba(99,102,241,0.10), transparent 70%);
          top: -160px; left: -120px;
          animation: orb-drift 9s ease-in-out infinite;
        }
        .orb-2 {
          width: 360px; height: 360px;
          background: radial-gradient(circle, rgba(14,165,233,0.08), transparent 70%);
          bottom: -80px; right: -60px;
          animation: orb-drift 11s ease-in-out infinite reverse;
        }
        @keyframes orb-drift {
          0%, 100% { transform: translateY(0px) scale(1); }
          50%       { transform: translateY(-18px) scale(1.04); }
        }

        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 0.375rem;
          padding: 0.3rem 0.875rem;
          background: var(--primary-light);
          color: var(--primary);
          border-radius: var(--radius-full);
          font-size: 0.8rem;
          font-weight: 600;
          border: 1px solid rgba(99,102,241,0.2);
          box-shadow: 0 2px 8px var(--primary-glow);
        }
        .hero-title {
          font-size: clamp(2rem, 5vw, 3rem);
          font-weight: 800;
          letter-spacing: -0.035em;
          line-height: 1.15;
          color: var(--text);
        }
        .hero-sub {
          font-size: 1.05rem;
          color: var(--text-muted);
          line-height: 1.7;
          max-width: 520px;
        }
        .hero-actions {
          display: flex;
          gap: 0.75rem;
          flex-wrap: wrap;
          justify-content: center;
          margin-top: 0.25rem;
        }
        .hero-btn {
          padding: 0.75rem 1.625rem;
          font-size: 1rem;
        }

        /* Flow steps */
        .flow-section { }
        .flow-steps {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          flex-wrap: wrap;
          padding: 1.25rem 1.5rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          box-shadow: var(--shadow-xs);
        }
        .flow-step {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        .flow-num {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          background: var(--gradient-primary);
          color: #fff;
          font-size: 0.85rem;
          font-weight: 700;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }
        .flow-text {
          display: flex;
          flex-direction: column;
        }
        .flow-label {
          font-size: 0.9rem;
          font-weight: 700;
          color: var(--text);
          line-height: 1.3;
        }
        .flow-sub {
          font-size: 0.75rem;
          color: var(--text-light);
        }
        .flow-arrow {
          color: var(--text-light);
          flex-shrink: 0;
        }

        /* Features */
        .section-eyebrow {
          font-size: 0.78rem;
          font-weight: 700;
          letter-spacing: 0.1em;
          color: var(--primary);
          text-transform: uppercase;
          margin-bottom: 1rem;
        }
        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 1.25rem;
        }
        .feature-card {
          padding: 1.75rem;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          cursor: pointer;
          text-decoration: none;
          transition: box-shadow 0.22s ease, border-color 0.22s ease, transform 0.22s ease;
        }
        .feature-card:hover {
          box-shadow: 0 10px 32px var(--feat-glow, rgba(99,102,241,0.15)), var(--shadow-md);
          border-color: rgba(99,102,241,0.18);
          transform: translateY(-4px);
        }
        .feat-icon-wrap {
          width: 52px;
          height: 52px;
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.22s ease;
        }
        .feature-card:hover .feat-icon-wrap { transform: scale(1.08); }

        .feat-primary  { background: var(--primary-light);   color: var(--primary);   }
        .feat-secondary{ background: var(--secondary-light); color: var(--secondary); }
        .feat-accent   { background: #fff1f2;                color: #f43f5e;          }

        .feat-title {
          font-size: 1.05rem;
          font-weight: 700;
          color: var(--text);
        }
        .feat-desc {
          font-size: 0.9rem;
          color: var(--text-muted);
          line-height: 1.6;
          flex: 1;
        }
        .feat-link {
          display: inline-flex;
          align-items: center;
          gap: 0.3rem;
          font-size: 0.85rem;
          font-weight: 600;
          color: var(--primary);
          margin-top: 0.25rem;
          transition: gap 0.18s ease;
        }
        .feature-card:hover .feat-link { gap: 0.5rem; }
      `}</style>
    </div>
  );
};

export default Home;
