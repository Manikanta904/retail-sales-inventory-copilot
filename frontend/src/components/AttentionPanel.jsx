import React, { useState } from 'react';
import AttentionCard from './AttentionCard';
import { AlertCircle, Filter, CheckCircle2 } from 'lucide-react';

export default function AttentionPanel({
  summaryData,
  selectedIssueFilter = 'ALL',
  onSelectIssueFilter,
}) {
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [filterStore, setFilterStore] = useState('ALL');
  const [filterCategory, setFilterCategory] = useState('ALL');

  if (!summaryData || !summaryData.items) {
    return (
      <div className="attention-section" id="attention-section">
        <div className="empty-state">
          <CheckCircle2 size={32} className="text-success" />
          <div>✓ No attention items identified for the latest available data.</div>
        </div>
      </div>
    );
  }

  const rawItems = summaryData.items;

  // Derive unique stores & categories from operational items for filtering
  const uniqueStores = Array.from(
    new Set(rawItems.map((i) => i.store_name || i.store_id).filter(Boolean))
  ).sort();

  const uniqueCategories = Array.from(
    new Set(rawItems.map((i) => i.category).filter(Boolean))
  ).sort();

  // Priority mapping according to prompt section 4.D
  const priorityRank = {
    OUT_OF_STOCK: 1,
    CRITICAL_STOCK_OUT_RISK: 2,
    LOW_STOCK: 3,
    OVERSTOCKED_SLOW_MOVING: 4,
    OVERSTOCKED: 4,
    SALES_DROP: 5,
    SALES_SPIKE: 6,
  };

  // Sort items by priority
  const sortedItems = [...rawItems].sort((a, b) => {
    const rankA = priorityRank[a.issue_type] || 99;
    const rankB = priorityRank[b.issue_type] || 99;
    if (rankA !== rankB) return rankA - rankB;
    // Secondary sort by severity (HIGH before MEDIUM before LOW)
    const sevRank = { HIGH: 1, MEDIUM: 2, LOW: 3 };
    const sevA = sevRank[(a.severity || 'MEDIUM').toUpperCase()] || 2;
    const sevB = sevRank[(b.severity || 'MEDIUM').toUpperCase()] || 2;
    return sevA - sevB;
  });

  const activeIssueFilter = selectedIssueFilter || 'ALL';

  const filteredItems = sortedItems.filter((item) => {
    // Severity filter
    if (filterSeverity !== 'ALL' && (item.severity || '').toUpperCase() !== filterSeverity) {
      return false;
    }
    // Issue type filter
    if (activeIssueFilter !== 'ALL') {
      const issue = (item.issue_type || '').toUpperCase();
      if (activeIssueFilter === 'STOCKOUT' && issue !== 'OUT_OF_STOCK') return false;
      if (activeIssueFilter === 'CRITICAL_RISK' && issue !== 'CRITICAL_STOCK_OUT_RISK') return false;
      if (activeIssueFilter === 'LOW_STOCK' && issue !== 'LOW_STOCK') return false;
      if (activeIssueFilter === 'OVERSTOCK' && !issue.includes('OVERSTOCKED') && !issue.includes('SLOW_MOVING')) return false;
      if (activeIssueFilter === 'SPIKE' && issue !== 'SALES_SPIKE') return false;
      if (activeIssueFilter === 'DROP' && issue !== 'SALES_DROP') return false;
    }
    // Store filter
    if (filterStore !== 'ALL') {
      const sName = item.store_name || item.store_id;
      if (sName !== filterStore && item.store_id !== filterStore) return false;
    }
    // Category filter
    if (filterCategory !== 'ALL' && item.category !== filterCategory) {
      return false;
    }
    return true;
  });

  return (
    <div className="attention-section" id="attention-section">
      <div className="section-header">
        <div className="section-title">
          <AlertCircle size={20} className="text-primary" />
          Items Requiring Operational Attention ({filteredItems.length})
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
          {/* Issue Type Filter Selector */}
          <select
            className="select-input"
            style={{ fontSize: '0.8125rem', padding: '0.35rem 0.65rem' }}
            value={activeIssueFilter}
            onChange={(e) => onSelectIssueFilter && onSelectIssueFilter(e.target.value)}
          >
            <option value="ALL">All Issue Types</option>
            <option value="STOCKOUT">Out of Stock</option>
            <option value="CRITICAL_RISK">Stock-out Risk (&lt; 7 Days)</option>
            <option value="LOW_STOCK">Low Stock Warnings</option>
            <option value="OVERSTOCK">Overstock &amp; Slow Moving</option>
            <option value="SPIKE">Sales Spikes (&ge; 1.8x)</option>
            <option value="DROP">Sales Drops (&le; 0.4x)</option>
          </select>

          {/* Store Filter Selector */}
          <select
            className="select-input"
            style={{ fontSize: '0.8125rem', padding: '0.35rem 0.65rem' }}
            value={filterStore}
            onChange={(e) => setFilterStore(e.target.value)}
          >
            <option value="ALL">All Stores</option>
            {uniqueStores.map((sName, idx) => (
              <option key={idx} value={sName}>
                {sName}
              </option>
            ))}
          </select>

          {/* Category Filter Selector */}
          <select
            className="select-input"
            style={{ fontSize: '0.8125rem', padding: '0.35rem 0.65rem' }}
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="ALL">All Categories</option>
            {uniqueCategories.map((cat, idx) => (
              <option key={idx} value={cat}>
                {cat}
              </option>
            ))}
          </select>

          {/* Severity Pills */}
          <div className="filter-pills">
            <button
              className={`pill-btn ${filterSeverity === 'ALL' ? 'active' : ''}`}
              onClick={() => setFilterSeverity('ALL')}
            >
              All ({summaryData.total_attention_items || rawItems.length})
            </button>
            <button
              className={`pill-btn ${filterSeverity === 'HIGH' ? 'active' : ''}`}
              onClick={() => setFilterSeverity('HIGH')}
            >
              High ({summaryData.high_severity_count || 0})
            </button>
            <button
              className={`pill-btn ${filterSeverity === 'MEDIUM' ? 'active' : ''}`}
              onClick={() => setFilterSeverity('MEDIUM')}
            >
              Medium ({summaryData.medium_severity_count || 0})
            </button>
            <button
              className={`pill-btn ${filterSeverity === 'LOW' ? 'active' : ''}`}
              onClick={() => setFilterSeverity('LOW')}
            >
              Low ({summaryData.low_severity_count || 0})
            </button>
          </div>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="empty-state">
          <Filter size={24} />
          <div>✓ No attention items match the selected filter criteria.</div>
        </div>
      ) : (
        <div className="attention-grid">
          {filteredItems.map((item, idx) => (
            <AttentionCard key={idx} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}

