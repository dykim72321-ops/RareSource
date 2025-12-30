import React from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  onSearch?: (query: string) => void;
  showSearch?: boolean;
}

const Header: React.FC<HeaderProps> = ({ onSearch, showSearch = true }) => {
  const navigate = useNavigate();
  const [query, setQuery] = React.useState('');
  const [menuOpen, setMenuOpen] = React.useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch && query.trim()) {
      onSearch(query);
    }
  };

  return (
    <header className="app-header">
      <div className="header-logo" onClick={() => navigate('/')}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polygon points="12 2 2 7 12 12 22 7 12 2" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
        RARE SOURCE
      </div>

      {showSearch && (
        <div className="header-search">
          <form onSubmit={handleSearch} style={{ position: 'relative' }}>
            <input
              type="text"
              className="search-bar"
              placeholder="Search part number..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ width: '100%', padding: '0.75rem 1rem' }}
            />
            <button type="submit" className="search-btn" style={{ fontSize: '0.9rem' }}>
              Search
            </button>
          </form>
        </div>
      )}

      <div className="header-actions">
        <button className="hamburger-menu" onClick={() => setMenuOpen(!menuOpen)}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
      </div>

      {menuOpen && (
        <div style={{
          position: 'absolute',
          top: 'var(--header-height)',
          right: '2rem',
          background: 'white',
          border: '1px solid var(--border)',
          borderRadius: '0.75rem',
          padding: '1rem',
          boxShadow: 'var(--shadow-lg)',
          minWidth: '200px',
          zIndex: 1000
        }}>
          <div style={{ padding: '0.75rem', cursor: 'pointer', borderBottom: '1px solid var(--border-light)' }}>
            Electronic Parts
          </div>
          <div style={{ padding: '0.75rem', cursor: 'pointer', borderBottom: '1px solid var(--border-light)' }}>
            Distributors
          </div>
          <div style={{ padding: '0.75rem', cursor: 'pointer', borderBottom: '1px solid var(--border-light)' }}>
            Manufacturers
          </div>
          <div style={{ padding: '0.75rem', cursor: 'pointer' }}>
            API
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
