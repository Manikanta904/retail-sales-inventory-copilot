import React from 'react';
import { Lightbulb, ArrowRight } from 'lucide-react';

export default function RecommendationCard({ recommendations }) {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="section-box">
      <div className="box-title">
        <Lightbulb size={16} /> Recommended Store Actions (Advisory)
      </div>
      <div className="recommendations-grid">
        {recommendations.map((rec, idx) => {
          const priority = (rec.priority || 'MEDIUM').toUpperCase();
          return (
            <div key={idx} className={`recommendation-card ${priority}`}>
              <div className="rec-header">
                <span className="rec-action">{rec.action}</span>
                <span className={`severity-badge ${priority.toLowerCase()}`}>
                  {priority} Priority
                </span>
              </div>
              <div className="rec-impact">
                <ArrowRight size={12} style={{ display: 'inline', marginRight: 4 }} />
                <strong>Expected Impact:</strong> {rec.expected_impact}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
