import React, { useState, useEffect } from 'react';

// --- Types ---
interface ComponentPart {
  id: string;
  mpn: string;
  manufacturer: string;
  distributor: string;
  source_type: string;
  stock: number;
  price: number;
  price_history: number[];
  basePrice?: number;
  currency: string;
  delivery: string;
  condition: string;
  date_code: string;
  is_eol: boolean;
  risk_level: string;
  is_qc_enabled?: boolean;
}

interface MarketStats {
  market_temperature: string;
  global_stock_index: number;
  active_brokers: number;
  price_drift: number;
  last_sync: string;
  recent_logs: string[];
}

type JourneyPhase = 'IDLE' | 'SCOUTING' | 'RESULTS';

const QC_PRICE = 72500;

const App: React.FC = () => {
  const [phase, setPhase] = useState<JourneyPhase>('IDLE');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ComponentPart[]>([]);
  const [history, setHistory] = useState<string[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedPart, setSelectedPart] = useState<ComponentPart | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);
  const [marketStats, setMarketStats] = useState<MarketStats | null>(null);
  const [trackingId, setTrackingId] = useState<string | null>(null);

  // --- Logic ---
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('http://localhost:8000/market/stats');
        if (response.ok) {
          const data = await response.json();
          setMarketStats(data);
        }
      } catch (err) {
        console.error("Failed to sync market intellect");
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (e?: React.FormEvent, historicalQuery?: string) => {
    if (e) e.preventDefault();
    const targetQuery = historicalQuery || query;
    if (!targetQuery.trim()) return;

    setPhase('SCOUTING');
    setError(null);
    setLogs([]); // Clear previous logs
    
    // Initial logs simulation
    setLogs(["[BOOT] Initializing Intel Engine...", "[OSINT] Checking Global Broker Manifests...", "[SCANNING] Secondary Market Clusters..."]);

    try {
      const [response] = await Promise.all([
        fetch(`http://localhost:8000/search?q=${encodeURIComponent(targetQuery)}`),
        new Promise(resolve => setTimeout(resolve, 3500))
      ]);
      
      if (!response.ok) throw new Error('System link failure');
      const data: ComponentPart[] = await response.json();
      
      setResults(data.map(item => ({ ...item, basePrice: item.price, is_qc_enabled: false })));
      if (!history.includes(targetQuery)) setHistory(prev => [targetQuery, ...prev].slice(0, 5));
      setPhase('RESULTS');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown System Error');
      setPhase('IDLE');
    }
  };

  const toggleQC = (id: string, current: boolean) => {
    setResults(prev => prev.map(item => {
      if (item.id === id) {
        const newState = !current;
        return {
          ...item,
          is_qc_enabled: newState,
          price: newState ? (item.basePrice || item.price) + QC_PRICE : (item.basePrice || item.price)
        };
      }
      return item;
    }));
  };

  const handleLock = async (part: ComponentPart) => {
    setSelectedPart(part);
    try {
      const response = await fetch('http://localhost:8000/procurement/lock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ part_id: part.id, quantity: 1 })
      });
      if (response.ok) {
        const data = await response.json();
        setTrackingId(data.tracking_id);
        setShowSuccess(true);
      }
    } catch (err) {
      alert("Security protocol violation during lock sequence.");
    }
  };

  // --- Visual Helpers ---
  const Sparkline = ({ data }: { data: number[] }) => {
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min;
    return (
      <div className="sparkline" style={{ display: 'flex', alignItems: 'flex-end', gap: '2px', height: '20px' }}>
        {data.map((v, i) => (
          <div key={i} style={{ 
            width: '4px', 
            height: `${((v - min) / range) * 100}%`, 
            background: 'var(--accent)',
            opacity: 0.3 + (i / data.length) * 0.7 
          }} />
        ))}
      </div>
    );
  };

  // --- Render Components ---

  const renderSidebar = () => (
    <aside className="sidebar">
      <div className="logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polygon points="12 2 2 7 12 12 22 7 12 2" />
          <polyline points="2 17 12 22 22 17" />
          <polyline points="2 12 12 17 22 12" />
        </svg>
        RARE SOURCE
      </div>

      <nav>
        <div className="nav-section-title">Mission History</div>
        <div className="filter-group">
          {history.length === 0 ? (
            <div style={{ padding: '0 0.5rem', color: 'var(--text-muted)', fontSize: '0.75rem' }}>No recent missions</div>
          ) : (
            history.map(h => (
              <div key={h} className="filter-item" onClick={() => handleSearch(undefined, h)}>
                🛰️ {h.toUpperCase()}
              </div>
            ))
          )}
        </div>
      </nav>

      <nav>
        <div className="nav-section-title">Market Intel</div>
        <div className="filter-group">
          <div className="filter-item active">Global Inventory</div>
          <div className="filter-item">EOL Risk Map</div>
          <div className="filter-item">Price Volatility</div>
        </div>
      </nav>

      {marketStats && (
        <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(255,255,255,0.03)', borderRadius: '0.75rem', fontSize: '0.75rem' }}>
          <div style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>GLOBAL INDEX</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
            <span>Stock</span>
            <span style={{ color: 'white' }}>{marketStats.global_stock_index.toLocaleString()}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span>Brokers</span>
            <span style={{ color: 'white' }}>{marketStats.active_brokers} Active</span>
          </div>
        </div>
      )}
    </aside>
  );

  const renderTopBar = () => (
    <div className="top-bar">
      <div style={{ display: 'flex', gap: '2rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
        <span>MARKET STATUS: <span style={{ color: marketStats?.market_temperature === 'CRITICAL' ? 'var(--danger)' : 'var(--success)', fontWeight: 'bold' }}>
          {marketStats?.market_temperature || 'SYNCING...'}
        </span></span>
        <span>PRICE DRIFT: <span style={{ color: (marketStats?.price_drift || 0) > 0 ? 'var(--warning)' : 'var(--success)' }}>
          {marketStats?.price_drift || 0}%
        </span></span>
      </div>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button className="filter-item" style={{ border: '1px solid var(--border-light)' }}>Export Intel</button>
      </div>
    </div>
  );

  const renderHero = () => (
    <section className={`hero-section ${phase !== 'IDLE' ? 'compact' : ''}`}>
      <div className="container">
        {phase === 'IDLE' && <h1>Scout the Unfindable.</h1>}
        <div className="search-container">
          <form onSubmit={handleSearch}>
            <input
              className="search-bar"
              placeholder="Inject MPN (e.g. TMS320C25)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button type="submit" className="search-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </section>
  );

  const renderScouting = () => (
    <div className="scout-container fade-in">
      <div className="radar-premium">
        <div className="scanning-line"></div>
      </div>
      <h2 style={{ letterSpacing: '0.3em', fontSize: '1.2rem', color: 'var(--accent)' }}>SATELLITE SYNC IN PROGRESS</h2>
      
      <div className="terminal-feed" style={{ marginTop: '2rem', height: '100px', width: '400px', background: 'rgba(0,0,0,0.5)', borderRadius: '0.5rem', padding: '1rem', overflowY: 'hidden', fontStyle: 'mono', fontSize: '0.7rem', border: '1px solid rgba(255,255,255,0.05)' }}>
        {logs.map((log, i) => (
          <div key={i} style={{ color: 'var(--success)', opacity: 0.5 + (i / logs.length) * 0.5, marginBottom: '0.2rem' }}>
            {log}
          </div>
        ))}
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="container fade-in">
      <div className="results-grid">
        {results.map(part => (
          <div key={part.id} className="card">
            <div className="card-header">
              <div>
                <div className="mpn">{part.mpn}</div>
                <div className="manufacturer">{part.manufacturer}</div>
              </div>
              <span className="stock-badge">{part.stock.toLocaleString()} UNITS</span>
            </div>

            <table className="data-table">
              <tbody>
                <tr><td className="label-cell">Source Access</td><td className="value-cell">{part.distributor}</td></tr>
                <tr><td className="label-cell">Risk Assessment</td><td className={`value-cell badge-risk-${part.risk_level.toLowerCase()}`}>{part.risk_level}</td></tr>
                <tr><td className="label-cell">Trend (7D)</td><td className="value-cell"><Sparkline data={part.price_history} /></td></tr>
                <tr><td className="label-cell">Verification</td><td className="value-cell">{part.condition} / {part.date_code}</td></tr>
              </tbody>
            </table>

            {(part.risk_level === 'Medium' || part.risk_level === 'High') && (
              <div style={{ border: '1px dashed var(--success)', padding: '1rem', borderRadius: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--success)' }}>QC Protocol +₩72,500</span>
                <input type="checkbox" checked={part.is_qc_enabled} onChange={() => toggleQC(part.id, !!part.is_qc_enabled)} />
              </div>
            )}

            <div className="pricing-row">
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>SECURE PRICE</div>
                <div className="price-main">
                  {part.price.toLocaleString()}<span className="currency">KRW</span>
                </div>
              </div>
              <button className="buy-btn" style={{ width: 'auto', padding: '1rem 2rem' }} onClick={() => handleLock(part)}>
                LOCK STOCK
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="app-wrapper">
      {renderSidebar()}
      
      <main className="main-content">
        {renderTopBar()}
        {renderHero()}

        <section style={{ paddingBottom: '5rem' }}>
          {error && <div className="container" style={{ color: 'var(--danger)', textAlign: 'center' }}>[TERMINAL_ERROR] {error}</div>}
          {phase === 'SCOUTING' && renderScouting()}
          {phase === 'RESULTS' && renderResults()}
        </section>
      </main>

      {showSuccess && (
        <div className="modal-overlay" onClick={() => setShowSuccess(false)}>
          <div className="modal">
            <div className="status-icon">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="4">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>INVENTORY SECURED</h2>
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '0.5rem', marginBottom: '2rem' }}>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>TRACKING INTEL ID</div>
              <div style={{ fontStyle: 'mono', color: 'var(--accent)', fontWeight: 'bold' }}>{trackingId}</div>
            </div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', lineHeight: '1.6' }}>
              Procurement lock initiated for MPN: <strong>{selectedPart?.mpn}</strong>.<br/>
              Shipment authorization is pending financial clearance.
            </p>
            <button className="buy-btn" onClick={() => { setShowSuccess(false); setPhase('IDLE'); }}>
              RETURN TO COMMAND CENTER
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
