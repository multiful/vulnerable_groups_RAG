import React from 'react';
import { ArrowRight, ShieldAlert, Award, Map as MapIcon } from 'lucide-react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="home-container">
      <section className="hero">
        <h1 className="hero-title">
          청년 위험군 맞춤형 <br />
          <span className="gradient-text">자격증 추천 및 로드맵 설계</span>
        </h1>
        <p className="hero-subtitle">
          상태에 맞는 현실적인 목표를 설정하고, 단계별로 성장할 수 있는 길을 찾아보세요.
        </p>
        <Link to="/risk-assessment" className="btn-primary hero-btn">
          시작하기 <ArrowRight size={20} />
        </Link>
      </section>

      <section className="features-grid">
        <div className="glass-card feature-card">
          <div className="feature-icon bg-primary-light">
            <ShieldAlert size={28} color="var(--primary)" />
          </div>
          <h3>위험군 진단</h3>
          <p className="feature-desc">현재 상태를 정확히 진단하고, 그에 맞는 현실적인 목표를 설정합니다.</p>
        </div>
        
        <div className="glass-card feature-card">
          <div className="feature-icon bg-secondary-light">
            <Award size={28} color="var(--secondary)" />
          </div>
          <h3>맞춤형 자격증</h3>
          <p className="feature-desc">진단 결과와 관심 직무/도메인을 바탕으로 최적의 자격증을 추천합니다.</p>
        </div>

        <div className="glass-card feature-card">
          <div className="feature-icon bg-accent-light">
            <MapIcon size={28} color="var(--accent)" />
          </div>
          <h3>성장 로드맵</h3>
          <p className="feature-desc">추천된 자격증을 취득하기 위한 단계별 구체적인 학습 경로를 제공합니다.</p>
        </div>
      </section>

      <style>{`
        .home-container {
          display: flex;
          flex-direction: column;
          gap: 4rem;
          padding-top: 2rem;
        }
        .hero {
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1.5rem;
          max-width: 800px;
          margin: 0 auto;
        }
        .hero-title {
          font-size: 3.5rem;
          line-height: 1.2;
          font-weight: 800;
          letter-spacing: -0.025em;
        }
        .hero-subtitle {
          font-size: 1.25rem;
          color: var(--text-muted);
          max-width: 600px;
        }
        .hero-btn {
          margin-top: 1rem;
          padding: 1rem 2rem;
          font-size: 1.125rem;
        }
        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 2rem;
        }
        .feature-card {
          padding: 2rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          transition: var(--transition);
        }
        .feature-card:hover {
          transform: translateY(-5px);
          border-color: rgba(99, 102, 241, 0.3);
        }
        .feature-icon {
          width: 3.5rem;
          height: 3.5rem;
          border-radius: 1rem;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 0.5rem;
        }
        .bg-primary-light { background: rgba(99, 102, 241, 0.15); }
        .bg-secondary-light { background: rgba(6, 182, 212, 0.15); }
        .bg-accent-light { background: rgba(244, 63, 94, 0.15); }
        .feature-desc {
          color: var(--text-muted);
          line-height: 1.6;
        }
      `}</style>
    </div>
  );
};

export default Home;
