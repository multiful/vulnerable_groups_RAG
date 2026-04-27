import React from 'react';
import { ArrowRight, ShieldAlert, Award, Map as MapIcon, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const FEATURES = [
  {
    icon: <ShieldAlert size={26} />,
    title: '위험군 진단',
    desc: '현재 취업 상태를 5단계로 진단하고 현실적인 목표를 설정합니다.',
    colorClass: 'feat-primary',
    glowColor: 'rgba(99,102,241,0.15)',
    path: '/risk-assessment',
  },
  {
    icon: <Award size={26} />,
    title: '맞춤 자격증',
    desc: '진단 결과와 관심 직무를 바탕으로 최적의 자격증을 추천합니다.',
    colorClass: 'feat-secondary',
    glowColor: 'rgba(14,165,233,0.15)',
    path: '/recommendation',
  },
  {
    icon: <MapIcon size={26} />,
    title: '성장 로드맵',
    desc: '목표 자격증 취득까지 단계별 학습 경로를 제공합니다.',
    colorClass: 'feat-accent',
    glowColor: 'rgba(244,63,94,0.12)',
    path: '/roadmap',
  },
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
            <span>청년 취업 지원 서비스</span>
          </div>
          <h1 className="hero-title">
            나에게 맞는 자격증과<br />
            <span className="gradient-text">단계별 성장 로드맵</span>
          </h1>
          <p className="hero-sub">
            취업 위험군 진단부터 자격증 추천, 학습 로드맵까지 한 번에.<br />
            지금 상황에서 시작할 수 있는 가장 현실적인 길을 찾아드립니다.
          </p>
          <div className="hero-actions">
            <Link to="/risk-assessment" className="btn-primary hero-btn">
              지금 시작하기 <ArrowRight size={18} />
            </Link>
            <Link to="/recommendation" className="btn-ghost hero-btn">
              자격증 둘러보기
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section>
        <p className="section-eyebrow">어떻게 도와드릴까요</p>
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
          background: radial-gradient(circle, rgba(99,102,241,0.14), transparent 70%);
          top: -160px; left: -120px;
          animation: orb-drift 9s ease-in-out infinite;
        }
        .orb-2 {
          width: 360px; height: 360px;
          background: radial-gradient(circle, rgba(14,165,233,0.11), transparent 70%);
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
