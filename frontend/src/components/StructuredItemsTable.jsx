import React, { useState } from 'react';
import { Package, AlertCircle, TrendingUp, Store, ChevronDown, ChevronUp } from 'lucide-react';

export default function StructuredItemsTable({ items }) {
  const [showAll, setShowAll] = useState(false);

  if (!items || items.length === 0) return null;

  const firstItem = items[0];
  const isStoreInfo = firstItem.location !== undefined && firstItem.type !== undefined && firstItem.total_revenue === undefined;
  const isCatalogInfo = firstItem.unit_price !== undefined && firstItem.reorder_point !== undefined;
  const isStorePerformance = firstItem.total_revenue !== undefined && firstItem.transactions_count !== undefined;
  const isStockout = ['OUT_OF_STOCK', 'CRITICAL_STOCK_OUT_RISK', 'LOW_STOCK'].includes(firstItem.status || firstItem.issue_type);
  const isOverstock = ['OVERSTOCKED', 'SLOW_MOVING', 'OVERSTOCKED_SLOW_MOVING'].includes(firstItem.status || firstItem.issue_type);
  const isAnomaly = ['SALES_SPIKE', 'SALES_DROP'].includes(firstItem.event_type || firstItem.status || firstItem.issue_type);
  const isPerformance = !isStoreInfo && !isCatalogInfo && !isStorePerformance && !isStockout && !isOverstock && !isAnomaly && (firstItem.revenue !== undefined && firstItem.revenue !== null);

  const displayItems = showAll ? items : items.slice(0, 5);
  const hasMore = items.length > 5;

  let title = 'Actionable Retail Intelligence Items';
  if (isStoreInfo) title = 'STORE NETWORK';
  else if (isCatalogInfo) title = 'PRODUCT CATALOG';
  else if (isStorePerformance) title = 'STORE PERFORMANCE SUMMARY';
  else if (isStockout) title = 'PRODUCTS REQUIRING REPLENISHMENT';
  else if (isOverstock) title = 'OVERSTOCKED & SLOW-MOVING INVENTORY';
  else if (isAnomaly) title = 'SALES VOLUME ANOMALIES';
  else if (isPerformance) title = 'PRODUCT PERFORMANCE';

  return (
    <div className="section-box">
      <div className="box-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', letterSpacing: '0.03em' }}>
          {isStoreInfo || isStorePerformance ? (
            <Store size={16} className="text-primary" />
          ) : isStockout ? (
            <AlertCircle size={16} className="text-danger" />
          ) : isAnomaly ? (
            <TrendingUp size={16} className="text-primary" />
          ) : (
            <Package size={16} className="text-primary" />
          )}
          {title}
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>
          {showAll ? `Showing all ${items.length} records` : `Showing ${displayItems.length} of ${items.length} records`}
        </span>
      </div>

      <div className="evidence-table-wrap" style={{ marginTop: '0.75rem' }}>
        <table className="evidence-table">
          <thead>
            {isStoreInfo && (
              <tr>
                <th>Store ID</th>
                <th>Store Name</th>
                <th>Location</th>
                <th>Region</th>
                <th>Type</th>
              </tr>
            )}
            {isCatalogInfo && (
              <tr>
                <th>Product ID</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Unit Price</th>
                <th>Unit Cost</th>
                <th>Reorder Point</th>
              </tr>
            )}
            {isStorePerformance && (
              <tr>
                <th>Store ID</th>
                <th>Store Name</th>
                <th>Location</th>
                <th>Total Revenue</th>
                <th>Units Sold</th>
                <th>Transactions</th>
                <th>Top Product</th>
              </tr>
            )}
            {isStockout && (
              <tr>
                <th>Product</th>
                <th>Store</th>
                <th>Stock</th>
                <th>Coverage</th>
                <th>Status</th>
                <th>Priority</th>
              </tr>
            )}
            {isOverstock && (
              <tr>
                <th>Product</th>
                <th>Store</th>
                <th>Stock</th>
                <th>Target Stock</th>
                <th>Sales Velocity</th>
                <th>Coverage</th>
                <th>Status</th>
              </tr>
            )}
            {isAnomaly && (
              <tr>
                <th>Product</th>
                <th>Store</th>
                <th>Event Type</th>
                <th>Recent Sales</th>
                <th>Baseline Sales</th>
                <th>Ratio / Change</th>
              </tr>
            )}
            {isPerformance && (
              <tr>
                <th>Product</th>
                <th>Period</th>
                <th>Units Sold</th>
                <th>Revenue</th>
                <th>Change %</th>
              </tr>
            )}
          </thead>
          <tbody>
            {displayItems.map((item, idx) => {
              const status = item.status || item.issue_type || item.event_type || 'NORMAL';
              const isHigh = status === 'OUT_OF_STOCK' || status === 'CRITICAL_STOCK_OUT_RISK' || status === 'OVERSTOCKED_SLOW_MOVING' || status === 'SALES_SPIKE';
              const isMed = status === 'LOW_STOCK' || status === 'OVERSTOCKED' || status === 'SLOW_MOVING' || status === 'SALES_DROP';

              const severityClass = isHigh ? 'high' : isMed ? 'medium' : 'low';
              const priorityLabel = isHigh ? 'HIGH' : isMed ? 'MEDIUM' : 'LOW';

              return (
                <tr key={idx}>
                  {/* Store Info Row */}
                  {isStoreInfo && (
                    <>
                      <td><strong>{item.store_id}</strong></td>
                      <td><div style={{ fontWeight: 600, color: 'var(--text)' }}>{item.store_name}</div></td>
                      <td>{item.location}</td>
                      <td>{item.region}</td>
                      <td><span className="source-tag">{item.type}</span></td>
                    </>
                  )}

                  {/* Catalog Info Row */}
                  {isCatalogInfo && (
                    <>
                      <td><strong>{item.product_id}</strong></td>
                      <td><div style={{ fontWeight: 600, color: 'var(--text)' }}>{item.product_name}</div></td>
                      <td><span className="source-tag">{item.category}</span></td>
                      <td>${item.unit_price?.toFixed(2)}</td>
                      <td>${(item.unit_cost || item.cost_price || 0).toFixed(2)}</td>
                      <td>{item.reorder_point} units</td>
                    </>
                  )}

                  {/* Store Performance Row */}
                  {isStorePerformance && (
                    <>
                      <td><strong>{item.store_id}</strong></td>
                      <td><div style={{ fontWeight: 600, color: 'var(--text)' }}>{item.store_name}</div></td>
                      <td>{item.location}</td>
                      <td><strong style={{ color: 'var(--primary)' }}>${item.total_revenue?.toLocaleString()}</strong></td>
                      <td>{item.units_sold} units</td>
                      <td>{item.transactions_count}</td>
                      <td>{item.top_selling_product}</td>
                    </>
                  )}

                  {/* Product Column for Standard Retail Items */}
                  {!isStoreInfo && !isCatalogInfo && !isStorePerformance && (
                    <>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text)' }}>
                          {item.product_name || item.product_id}
                        </div>
                        {item.product_id && (
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            {item.product_id}
                          </span>
                        )}
                      </td>

                      {/* Store Column */}
                      {item.store_name !== undefined && (
                        <td>
                          <div style={{ fontWeight: 500 }}>{item.store_name || item.store_id}</div>
                          {item.store_id && (
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                              {item.store_id}
                            </span>
                          )}
                        </td>
                      )}
                    </>
                  )}

                  {/* Stockout Specific Columns */}
                  {isStockout && (
                    <>
                      <td>
                        <strong style={{ color: item.stock_on_hand === 0 ? 'var(--danger)' : 'var(--text)' }}>
                          {item.stock_on_hand !== undefined ? `${item.stock_on_hand} units` : 'N/A'}
                        </strong>
                      </td>
                      <td>
                        <span className="metric-highlight">
                          {item.stock_coverage_days === 0 ? '0.00 days' : `${item.stock_coverage_days} days`}
                        </span>
                      </td>
                      <td>
                        <span className={`severity-badge ${severityClass}`}>
                          {status}
                        </span>
                      </td>
                      <td>
                        <span className={`severity-badge ${severityClass}`}>
                          {item.severity || priorityLabel}
                        </span>
                      </td>
                    </>
                  )}

                  {/* Overstock Specific Columns */}
                  {isOverstock && (
                    <>
                      <td>
                        <strong>{item.stock_on_hand} units</strong>
                      </td>
                      <td>{item.target_stock_level || 'N/A'} units</td>
                      <td>{item.avg_daily_sales} u/day</td>
                      <td>
                        <span className="metric-highlight">{item.stock_coverage_days} days</span>
                      </td>
                      <td>
                        <span className={`severity-badge ${severityClass}`}>
                          {status}
                        </span>
                      </td>
                    </>
                  )}

                  {/* Anomaly Specific Columns */}
                  {isAnomaly && (
                    <>
                      <td>
                        <span className={`severity-badge ${severityClass}`}>{status}</span>
                      </td>
                      <td>{item.recent_avg_daily_sales} u/day</td>
                      <td>{item.baseline_avg_daily_sales} u/day</td>
                      <td>
                        <strong>{item.sales_ratio}x</strong> ({item.percentage_change}%)
                      </td>
                    </>
                  )}

                  {/* Product Performance Columns */}
                  {isPerformance && (
                    <>
                      <td>30-Day Window</td>
                      <td>{item.units_sold} units</td>
                      <td>
                        <strong style={{ color: 'var(--primary)' }}>${item.revenue?.toLocaleString()}</strong>
                      </td>
                      <td>
                        <span className={`pill-btn ${item.revenue_change_pct >= 0 ? 'active' : ''}`}>
                          {item.revenue_change_pct >= 0 ? `+${item.revenue_change_pct}%` : `${item.revenue_change_pct}%`}
                        </span>
                      </td>
                    </>
                  )}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {hasMore && (
        <div style={{ marginTop: '0.75rem', textAlign: 'center' }}>
          <button
            className="nav-btn"
            onClick={() => setShowAll(!showAll)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem', margin: '0 auto', fontSize: '0.8125rem' }}
          >
            {showAll ? (
              <>
                Show top 5 <ChevronUp size={14} />
              </>
            ) : (
              <>
                Show all ({items.length}) <ChevronDown size={14} />
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}

