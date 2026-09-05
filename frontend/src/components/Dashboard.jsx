import React, { useState } from 'react';
import SummaryCards from './SummaryCards';
import AttentionPanel from './AttentionPanel';
import { RefreshCw, AlertCircle, BarChart3, Clock, Sparkles, ArrowRight, Lightbulb } from 'lucide-react';

export default function Dashboard({
  dashboardData,
  attentionData,
  loading,
  refreshing,
  error,
  lastRefreshed,
  onRefreshData,
  onOpenCopilot,
}) {
  const [selectedIssueFilter, setSelectedIssueFilter] = useState('ALL');

  if (loading && !dashboardData) {
    return (
      <div className="loading-state">
        <div className="loading-spinner"></div>
        <div>Loading store manager operational metrics from backend...</div>
      </div>
    );
  }

  if (error && !dashboardData) {
    return (
      <div className="error-state">
        <AlertCircle size={32} />
        <div>
          <strong>Unable to load Store Operational Command Center</strong>
          <p>{error}</p>
        </div>
        <button className="nav-btn active" onClick={onRefreshData} style={{ marginTop: '1rem' }}>
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  const handleBarClick = (filterCode) => {
    setSelectedIssueFilter(filterCode);
    const elem = document.getElementById('attention-section');
    if (elem) {
      elem.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Operational Risk Breakdown Items
  const chartItems = [
    { label: 'Out of Stock (0 units)', value: dashboardData?.out_of_stock_count || 0, colorClass: 'danger', filterCode: 'STOCKOUT' },
    { label: 'Critical Risk (< 7 days)', value: dashboardData?.critical_stock_out_risk_count || 0, colorClass: 'danger', filterCode: 'CRITICAL_RISK' },
    { label: 'Low Stock Warnings', value: dashboardData?.low_stock_warnings_count || 0, colorClass: 'warning', filterCode: 'LOW_STOCK' },
    { label: 'Overstocked Items', value: dashboardData?.overstocked_items_count || 0, colorClass: 'warning', filterCode: 'OVERSTOCK' },
    { label: 'Sales Spikes (>= 1.8x)', value: dashboardData?.spikes_detected_count || 0, colorClass: 'success', filterCode: 'SPIKE' },
    { label: 'Sales Drops (<= 0.4x)', value: dashboardData?.drops_detected_count || 0, colorClass: 'info', filterCode: 'DROP' },
  ];

  const maxChartVal = Math.max(...chartItems.map((item) => item.value), 1);

  // High severity out-of-stock items count for recommended manager actions banner
  const highRiskCount = (dashboardData?.out_of_stock_count || 0) + (dashboardData?.critical_stock_out_risk_count || 0);

  return (
    <div>
      {/* Header Operational Status */}
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title">Store Manager Operational Command Center</h1>
          <p className="page-desc">
            Deterministic stock coverage, replenishment priority, overstock, and sales velocity metrics grounded through{' '}
            <strong>{dashboardData?.date_range_end || 'Aug 29, 2026'}</strong>.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {lastRefreshed && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Clock size={13} /> Last refreshed: {lastRefreshed}
            </span>
          )}
          <button
            className="nav-btn active"
            onClick={onRefreshData}
            disabled={refreshing}
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <RefreshCw size={14} className={refreshing ? 'spinning' : ''} />
            {refreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <SummaryCards data={dashboardData} />

      {/* Operational Risk & Trend Breakdown Chart */}
      <div className="chart-card">
        <div className="chart-header">
          <div>
            <div className="chart-title">
              <BarChart3 size={20} className="text-primary" />
              Operational Risk &amp; Trend Breakdown
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
              Click any category bar to filter operational attention items below.
            </p>
          </div>
          <span className="card-subtext">Source: Python Deterministic Analytics</span>
        </div>

        <div className="chart-bars-container">
          {chartItems.map((bar, idx) => {
            const pct = Math.round((bar.value / maxChartVal) * 100);
            const isSelected = selectedIssueFilter === bar.filterCode;
            return (
              <div
                key={idx}
                className="chart-bar-row"
                onClick={() => handleBarClick(bar.filterCode)}
                title={`Click to filter attention table for ${bar.label}`}
                style={{
                  cursor: 'pointer',
                  padding: '0.4rem 0.6rem',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: isSelected ? 'var(--primary-light)' : 'transparent',
                  transition: 'background-color 0.15s ease',
                }}
              >
                <span className="chart-label" style={{ fontWeight: isSelected ? 700 : 500 }}>
                  {bar.label}
                </span>
                <div className="chart-bar-bg">
                  <div
                    className={`chart-bar-fill ${bar.colorClass}`}
                    style={{ width: `${pct}%` }}
                  ></div>
                </div>
                <span className="chart-val-num">{bar.value}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Primary Dedicated Copilot CTA Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, var(--surface), var(--surface-secondary))',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
          padding: '1.1rem 1.4rem',
          margin: '1.25rem 0',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          boxShadow: 'var(--shadow-sm)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div
            style={{
              background: 'var(--primary-light)',
              color: 'var(--primary)',
              padding: '0.5rem',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justify: 'center',
            }}
          >
            <Sparkles size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text)' }}>
              Need a deeper answer?
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>
              Ask the Retail Copilot about stockouts, overstock, sales trends, or store performance.
            </p>
          </div>
        </div>
        <button
          type="button"
          className="nav-btn active"
          onClick={(e) => {
            e.preventDefault();
            if (onOpenCopilot) onOpenCopilot();
          }}
          style={{
            cursor: 'pointer',
            background: 'linear-gradient(135deg, var(--primary), var(--accent))',
            color: 'white',
            fontWeight: 600,
            padding: '0.55rem 1.15rem',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-md)',
            border: 'none',
          }}
        >
          Open Retail Copilot <ArrowRight size={16} />
        </button>
      </div>

      {/* Manager Recommended Actions Area */}
      {highRiskCount > 0 && (
        <div
          className="chart-card"
          style={{
            marginBottom: '1.5rem',
            borderLeft: '4px solid var(--danger)',
            background: 'var(--surface)',
          }}
        >
          <div className="chart-header" style={{ marginBottom: '0.5rem' }}>
            <div className="chart-title">
              <Lightbulb size={18} className="text-warning" />
              Manager Recommended Operational Actions (Advisory)
            </div>
            <span className="card-subtext">Grounding Source: Deterministic Stock Thresholds</span>
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: '1.5' }}>
            • <strong>Immediate Reorder Priority:</strong> {dashboardData?.out_of_stock_count || 0} items are completely out of stock (0 units). Reorder immediately to restore shelf availability.
            <br />
            • <strong>Critical Stockout Risk Notice:</strong> {dashboardData?.critical_stock_out_risk_count || 0} items have less than 7 days of stock coverage based on recent daily sales velocity.
            <br />
            • <strong>Inventory Balancing:</strong> {dashboardData?.overstocked_items_count || 0} items hold excess stock exceeding 2.0x target levels. Review transfer options to high-demand stores.
          </div>
        </div>
      )}

      {/* Items Requiring Operational Attention */}
      <AttentionPanel
        summaryData={attentionData}
        selectedIssueFilter={selectedIssueFilter}
        onSelectIssueFilter={setSelectedIssueFilter}
      />
    </div>
  );
}

