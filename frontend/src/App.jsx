import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import Copilot from './components/Copilot';
import { getDashboard, getAttention, getProducts, getStores } from './api/api';
import { ShoppingBag, LayoutDashboard, Sparkles, Sun, Moon, Calendar, RefreshCw, CheckCircle2 } from 'lucide-react';
import './styles/app.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [initialCopilotQuestion, setInitialCopilotQuestion] = useState('');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('retail_copilot_theme') || 'light';
  });

  // App-level Shared In-Memory State
  const [dashboardData, setDashboardData] = useState(null);
  const [attentionData, setAttentionData] = useState(null);
  const [products, setProducts] = useState([]);
  const [stores, setStores] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState('');
  const [error, setError] = useState(null);
  const [lastRefreshed, setLastRefreshed] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('retail_copilot_theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const fetchAppData = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
      setRefreshMessage('Refreshing retail data...');
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      const [dash, att, prodList, stList] = await Promise.all([
        getDashboard(),
        getAttention(),
        getProducts(),
        getStores(),
      ]);

      setDashboardData(dash);
      setAttentionData(att);
      setProducts(prodList || []);
      setStores(stList || []);
      setLastRefreshed(new Date().toLocaleTimeString());

      if (isRefresh) {
        setRefreshMessage('Data refreshed');
        setTimeout(() => setRefreshMessage(''), 3000);
      }
    } catch (err) {
      setError(err.message || 'Failed to load retail intelligence metrics from backend service.');
      if (isRefresh) {
        setRefreshMessage('Failed to refresh data');
        setTimeout(() => setRefreshMessage(''), 4000);
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAppData(false);
  }, []);

  const handleRefreshData = () => {
    if (!refreshing) {
      fetchAppData(true);
    }
  };

  const handleOpenCopilot = (optQuestion = '') => {
    if (typeof optQuestion === 'string' && optQuestion.trim()) {
      setInitialCopilotQuestion(optQuestion);
    }
    setActiveTab('copilot');
  };

  return (
    <div className="app-container">
      {/* App Header Navigation Shell */}
      <header className="app-header">
        <div className="header-content">
          <div className="brand-section">
            <div className="brand-icon">
              <ShoppingBag size={24} />
            </div>
            <div>
              <div className="brand-title">Retail Intelligence Copilot</div>
              <div className="brand-subtitle">Sales &amp; Inventory Operational Command Center</div>
            </div>
          </div>

          <div className="nav-controls">
            {/* Navigation Tabs */}
            <nav className="nav-tabs">
              <button
                className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => setActiveTab('dashboard')}
              >
                <LayoutDashboard size={16} /> Operational Dashboard
              </button>
              <button
                className={`nav-btn ${activeTab === 'copilot' ? 'active' : ''}`}
                onClick={() => setActiveTab('copilot')}
              >
                <Sparkles size={16} /> Reasoning Copilot
              </button>
            </nav>

            {/* Refresh Data Button & Status Indicator */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                className="nav-btn"
                onClick={handleRefreshData}
                disabled={refreshing || loading}
                title="Explicitly refetch backend APIs and update shared state"
                style={{ border: '1px solid var(--border)', background: 'var(--surface-secondary)' }}
              >
                <RefreshCw size={14} className={refreshing ? 'spinning' : ''} />
                {refreshing ? 'Refreshing...' : 'Refresh Data'}
              </button>
              {refreshMessage && (
                <span
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    color: refreshMessage === 'Data refreshed' ? 'var(--success)' : 'var(--text-muted)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                  }}
                >
                  {refreshMessage === 'Data refreshed' && <CheckCircle2 size={14} />}
                  {refreshMessage}
                </span>
              )}
            </div>

            {/* Data Recency Grounding Badge */}
            <div className="recency-badge">
              <Calendar size={14} />
              <span>Retail data through: {dashboardData?.date_range_end || '2026-08-29'}</span>
              {lastRefreshed && (
                <span style={{ opacity: 0.85, borderLeft: '1px solid var(--border)', paddingLeft: '0.35rem', marginLeft: '0.2rem' }}>
                  Last refreshed: {lastRefreshed}
                </span>
              )}
            </div>

            {/* Theme Toggle Button */}
            <button
              className="theme-btn"
              onClick={toggleTheme}
              title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
              aria-label="Toggle Theme"
            >
              {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="app-main">
        <div style={{ display: activeTab === 'dashboard' ? 'block' : 'none' }}>
          <Dashboard
            dashboardData={dashboardData}
            attentionData={attentionData}
            loading={loading}
            refreshing={refreshing}
            error={error}
            lastRefreshed={lastRefreshed}
            onRefreshData={handleRefreshData}
            onOpenCopilot={handleOpenCopilot}
          />
        </div>
        <div style={{ display: activeTab === 'copilot' ? 'block' : 'none' }}>
          <Copilot
            stores={stores}
            products={products}
            initialQuestion={initialCopilotQuestion}
          />
        </div>
      </main>
    </div>
  );
}

