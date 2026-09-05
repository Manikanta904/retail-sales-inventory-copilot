import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, Info, Tag, ChevronDown, ChevronUp } from 'lucide-react';

export default function AttentionCard({ item }) {
  const [expanded, setExpanded] = useState(false);

  if (!item) return null;

  const getSeverityBadge = (severity) => {
    const sev = (severity || 'MEDIUM').toUpperCase();
    if (sev === 'HIGH') {
      return (
        <span className="severity-badge high">
          <ShieldAlert size={14} /> High Severity
        </span>
      );
    }
    if (sev === 'MEDIUM') {
      return (
        <span className="severity-badge medium">
          <AlertTriangle size={14} /> Medium Severity
        </span>
      );
    }
    return (
      <span className="severity-badge low">
        <Info size={14} /> Low Severity
      </span>
    );
  };

  const getCardClass = (severity) => {
    const sev = (severity || 'MEDIUM').toLowerCase();
    return `attention-card ${sev}`;
  };

  const formatIssueType = (issue) => {
    if (!issue) return 'OPERATIONAL_ALERT';
    return issue.replace(/_/g, ' ');
  };

  return (
    <div className={getCardClass(item.severity)}>
      <div className="card-header-row">
        <div>
          <div className="prod-title">{item.product_name || item.product_id}</div>
          <div className="prod-meta">
            Store: {item.store_name || item.store_id} ({item.store_id}) | Product ID: {item.product_id}
          </div>
        </div>
        {getSeverityBadge(item.severity)}
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <span className="issue-tag">{formatIssueType(item.issue_type)}</span>
          {item.category && (
            <span className="prod-meta">
              <Tag size={12} style={{ display: 'inline', marginRight: 2 }} />
              {item.category}
            </span>
          )}
        </div>

        <button
          className="nav-btn"
          onClick={() => setExpanded(!expanded)}
          style={{
            fontSize: '0.75rem',
            padding: '0.2rem 0.5rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.25rem',
            color: 'var(--text-secondary)',
            fontWeight: 500,
            border: '1px solid var(--border)',
            background: 'var(--surface-secondary)',
            borderRadius: 'var(--radius-sm)',
          }}
        >
          {expanded ? (
            <>
              <ChevronUp size={13} /> Hide Details
            </>
          ) : (
            <>
              <ChevronDown size={13} /> View Details
            </>
          )}
        </button>
      </div>

      {item.metric_value && (
        <div className="metric-highlight">{item.metric_value}</div>
      )}

      {expanded && item.evidence && (
        <div className="evidence-text" style={{ marginTop: '0.5rem', animation: 'fadeIn 0.2s ease' }}>
          <strong>Operational Evidence:</strong> {item.evidence}
        </div>
      )}
    </div>
  );
}

