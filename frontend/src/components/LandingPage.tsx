import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import FeatureCard from './FeatureCard';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
    }
  };

  const features = [
    {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
          <path d="M2 12h20" />
        </svg>
      ),
      title: 'Global Scout Network',
      description: '전 세계 12개 이상의 브로커 네트워크를 실시간으로 스캔하여 희귀 부품을 발굴합니다.'
    },
    {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      ),
      title: 'Risk Assessment',
      description: '부품별 신뢰도와 리스크 레벨을 자동 분석하여 안전한 구매를 지원합니다.'
    },
    {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <polyline points="10 9 9 9 8 9" />
        </svg>
      ),
      title: 'QC Protocol',
      description: '신뢰할 수 없는 재고에 대한 정밀 검수 옵션을 추가하여 품질을 보장합니다.'
    },
    {
      icon: (
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
      ),
      title: 'Secure Transaction',
      description: '백투백 매입 주문 시뮬레이션으로 안전한 거래를 보장합니다.'
    }
  ];

  return (
    <div>
      {/* Hero Section */}
      <section className="landing-hero">
        <div className="landing-hero-content">
          <h1>희귀 부품 메타 검색 플랫폼</h1>
          <p>
            산업용 장비의 유지보수를 위한 희귀/단종 부품(EOL)을 전 세계 브로커 네트워크에서 발굴하세요
          </p>
          <div className="landing-search-large" style={{ position: 'relative' }}>
            <form onSubmit={handleSearch}>
              <input
                type="text"
                placeholder="부품 번호를 입력하세요 (예: TMS320...)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button type="submit">검색</button>
            </form>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <h2 className="features-title">핵심 기능</h2>
          <p className="features-subtitle">
            전문가급 부품 소싱을 위한 강력한 도구들
          </p>
          <div className="features-grid">
            {features.map((feature, index) => (
              <FeatureCard
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container">
          <div className="stat-item">
            <h3>12+</h3>
            <p>Active Brokers</p>
          </div>
          <div className="stat-item">
            <h3>50K+</h3>
            <p>Parts Database</p>
          </div>
          <div className="stat-item">
            <h3>99.9%</h3>
            <p>Uptime</p>
          </div>
          <div className="stat-item">
            <h3>24/7</h3>
            <p>Support</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <h2 className="cta-title">지금 바로 시작하세요</h2>
        <p className="cta-subtitle">
          필요한 부품을 빠르고 안전하게 찾아보세요
        </p>
        <button className="btn-primary" onClick={() => navigate('/search')}>
          검색 시작하기
        </button>
      </section>
    </div>
  );
};

export default LandingPage;
