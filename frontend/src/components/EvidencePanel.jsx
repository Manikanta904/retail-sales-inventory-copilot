import React from 'react';
import { Database } from 'lucide-react';

export default function EvidencePanel({ evidence, hideHeader = false }) {
  if (!evidence || evidence.length === 0) return null;

  return (
    <div className={hideHeader ? '' : 'section-box'}>
      {!hideHeader && (
        <div className="box-title">
          <Database size={16} /> Authoritative Numerical Evidence
        </div>
      )}
      <div className="evidence-table-wrap">
        <table className="evidence-table">
          <thead>
            <tr>
              <th>Source</th>
              <th>Metric</th>
              <th>Calculated Value</th>
              <th>Evidence Details</th>
            </tr>
          </thead>
          <tbody>
            {evidence.map((item, idx) => (
              <tr key={idx}>
                <td>
                  <span className="source-tag">{item.source}</span>
                </td>
                <td>
                  <strong>{item.metric}</strong>
                </td>
                <td>
                  <span className="issue-tag">{item.value}</span>
                </td>
                <td>{item.details}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
