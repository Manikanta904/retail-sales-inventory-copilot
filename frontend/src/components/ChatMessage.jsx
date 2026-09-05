import React, { useState } from 'react';
import EvidencePanel from './EvidencePanel';
import RecommendationCard from './RecommendationCard';
import StructuredItemsTable from './StructuredItemsTable';
import { Bot, User, AlertTriangle, FileText, CheckCircle2, HelpCircle, Database, ChevronDown, ChevronUp } from 'lucide-react';

export default function ChatMessage({ message }) {
  const [evidenceExpanded, setEvidenceExpanded] = useState(false);
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="chat-message user">
        <div className="avatar user">
          <User size={20} />
        </div>
        <div className="message-bubble">
          <p className="response-answer">{message.content}</p>
        </div>
      </div>
    );
  }

  const res = message.response;
  if (!res) return null;

  const isInsufficient = res.status === 'insufficient_data';
  const sm = res.summary_metrics || {};

  const firstItem = res.structured_items && res.structured_items.length > 0 ? res.structured_items[0] : null;
  const isSimpleFactual = (firstItem && (
    (firstItem.location !== undefined && firstItem.type !== undefined && firstItem.total_revenue === undefined) ||
    (firstItem.unit_price !== undefined && firstItem.reorder_point !== undefined)
  )) || (sm && sm.total_days !== undefined);

  return (
    <div className="chat-message assistant">
      <div className="avatar assistant">
        <Bot size={20} />
      </div>
      <div className="message-bubble" style={{ flex: 1 }}>
        {isInsufficient ? (
          /* Insufficient Data / Refusal UI */
          <div className="refusal-box">
            <div className="refusal-title">
              <AlertTriangle size={20} /> INSUFFICIENT DATA
            </div>
            <div className="refusal-text">{res.answer}</div>

            {res.missing_information && res.missing_information.length > 0 && (
              <div style={{ marginBottom: '0.75rem' }}>
                <strong style={{ fontSize: '0.8125rem', color: 'var(--text)' }}>
                  Missing Information / Unprocessable Elements:
                </strong>
                <ul className="findings-list" style={{ marginTop: '0.25rem' }}>
                  {res.missing_information.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}

            {res.available_information && res.available_information.length > 0 && (
              <div>
                <strong style={{ fontSize: '0.8125rem', color: 'var(--text)' }}>
                  Data available:
                </strong>
                <ul className="findings-list" style={{ marginTop: '0.25rem' }}>
                  {res.available_information.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          /* Success Response UI */
          <div className="copilot-response">
            {/* 1. Executive Short Answer */}
            {res.answer && (
              <div className="response-answer" style={{ whiteSpace: 'pre-line' }}>
                {res.answer}
              </div>
            )}

            {/* 2. Compact KPI Strip (for aggregate analytical questions) */}
            {!isSimpleFactual && sm && (sm.out_of_stock_count !== undefined || sm.spikes_count !== undefined) && (
              <div className="kpi-strip">
                {sm.out_of_stock_count !== undefined && (
                  <div className="kpi-card danger">
                    <div className="kpi-num">{sm.out_of_stock_count}</div>
                    <div className="kpi-title">OUT OF STOCK</div>
                  </div>
                )}
                {sm.critical_stock_out_risk_count !== undefined && (
                  <div className="kpi-card warning">
                    <div className="kpi-num">{sm.critical_stock_out_risk_count}</div>
                    <div className="kpi-title">CRITICAL RISK</div>
                  </div>
                )}
                {sm.low_stock_warnings_count !== undefined && (
                  <div className="kpi-card info">
                    <div className="kpi-num">{sm.low_stock_warnings_count}</div>
                    <div className="kpi-title">LOW STOCK</div>
                  </div>
                )}
                {sm.spikes_count !== undefined && (
                  <div className="kpi-card success">
                    <div className="kpi-num">{sm.spikes_count}</div>
                    <div className="kpi-title">SALES SPIKES</div>
                  </div>
                )}
                {sm.drops_count !== undefined && (
                  <div className="kpi-card info">
                    <div className="kpi-num">{sm.drops_count}</div>
                    <div className="kpi-title">SALES DROPS</div>
                  </div>
                )}
              </div>
            )}

            {/* 3. Question-Specific Actionable Table */}
            {res.structured_items && res.structured_items.length > 0 && (
              <StructuredItemsTable items={res.structured_items} />
            )}

            {/* 4. Key Analytical Findings (Analytical Questions Only) */}
            {!isSimpleFactual && res.findings && res.findings.length > 0 && (
              <div className="section-box">
                <div className="box-title">
                  <CheckCircle2 size={16} /> Key Analytical Findings
                </div>
                <ul className="findings-list">
                  {res.findings.map((f, idx) => (
                    <li key={idx}>{f}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* 5. Recommended Store Actions (Analytical Questions Only) */}
            {!isSimpleFactual && <RecommendationCard recommendations={res.recommendations} />}

            {/* 6. Analysis Assumptions (Analytical Questions Only) */}
            {!isSimpleFactual && res.assumptions && res.assumptions.length > 0 && (
              <div className="section-box" style={{ padding: '0.75rem 1rem' }}>
                <div className="box-title" style={{ fontSize: '0.8125rem', marginBottom: '0.35rem' }}>
                  <HelpCircle size={14} /> Analysis assumptions
                </div>
                <ul className="assumptions-list">
                  {res.assumptions.map((a, idx) => (
                    <li key={idx} style={{ fontSize: '0.8125rem' }}>
                      • <strong>{a.statement}:</strong> {a.basis}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* 7. Collapsible Authoritative Evidence (Analytical Questions Only) */}
            {!isSimpleFactual && res.evidence && res.evidence.length > 0 && (
              <div className="section-box" style={{ padding: '0.75rem 1rem' }}>
                <button
                  className="nav-btn"
                  onClick={() => setEvidenceExpanded(!evidenceExpanded)}
                  style={{
                    width: '100%',
                    justifyContent: 'space-between',
                    padding: 0,
                    background: 'transparent',
                    border: 'none',
                    fontWeight: 600,
                    color: 'var(--text)',
                  }}
                >
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Database size={15} className="text-primary" /> View calculation evidence ({res.evidence.length} items)
                  </span>
                  {evidenceExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {evidenceExpanded && (
                  <div style={{ marginTop: '0.75rem' }}>
                    <EvidencePanel evidence={res.evidence} hideHeader={true} />
                  </div>
                )}
              </div>
            )}

            {/* 8. Compact Grounded Data Sources Footer */}
            {res.data_sources && res.data_sources.length > 0 && (
              <div className="sources-row" style={{ fontSize: '0.75rem', marginTop: '0.25rem' }}>
                <FileText size={13} /> Grounded sources:
                {res.data_sources.map((src, idx) => (
                  <span key={idx} className="source-tag">
                    {src}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
