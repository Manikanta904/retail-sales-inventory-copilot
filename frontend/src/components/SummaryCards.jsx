import React from 'react';
import {
  Store,
  Package,
  ShoppingCart,
  DollarSign,
  AlertOctagon,
  AlertTriangle,
  Info,
  TrendingUp,
  TrendingDown,
  Box,
} from 'lucide-react';

export default function SummaryCards({ data }) {
  if (!data) return null;

  const formatCurrency = (val) => {
    if (val === undefined || val === null) return '$0.00';
    return `$${Number(val).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`;
  };

  const formatNumber = (val) => {
    if (val === undefined || val === null) return '0';
    return Number(val).toLocaleString();
  };

  const cards = [
    {
      label: 'Active Stores',
      value: formatNumber(data.total_stores),
      subtext: 'Retail Store Network',
      icon: Store,
      colorClass: 'primary',
    },
    {
      label: 'Product Catalog',
      value: formatNumber(data.total_products),
      subtext: 'Active SKUs',
      icon: Package,
      colorClass: 'accent',
    },
    {
      label: 'Total Revenue',
      value: formatCurrency(data.total_revenue_ytd),
      subtext: `Dataset period: ${data.date_range_start || 'Jun 1'} to ${data.date_range_end || 'Aug 29'}`,
      icon: DollarSign,
      colorClass: 'success',
    },
    {
      label: 'Transactions',
      value: formatNumber(data.total_sales_transactions),
      subtext: `${formatNumber(data.total_units_sold)} Total Units Sold`,
      icon: ShoppingCart,
      colorClass: 'info',
    },
    {
      label: 'Out of Stock',
      value: formatNumber(data.out_of_stock_count),
      subtext: 'Current 0 Stock Items',
      icon: AlertOctagon,
      colorClass: 'danger',
    },
    {
      label: 'Critical Risk',
      value: formatNumber(data.critical_stock_out_risk_count),
      subtext: '< 7.0 Days Coverage',
      icon: AlertTriangle,
      colorClass: 'danger',
    },
    {
      label: 'Low Stock',
      value: formatNumber(data.low_stock_warnings_count),
      subtext: '<= Reorder Point',
      icon: Info,
      colorClass: 'warning',
    },
    {
      label: 'Overstocked',
      value: formatNumber(data.overstocked_items_count),
      subtext: '>= 2.0x Target Stock Level',
      icon: Box,
      colorClass: 'warning',
    },
    {
      label: 'Sales Spikes',
      value: formatNumber(data.spikes_detected_count),
      subtext: '>= 1.8x Baseline Ratio',
      icon: TrendingUp,
      colorClass: 'success',
    },
    {
      label: 'Sales Drops',
      value: formatNumber(data.drops_detected_count),
      subtext: '<= 0.4x Baseline Ratio',
      icon: TrendingDown,
      colorClass: 'danger',
    },
  ];

  return (
    <div className="summary-grid">
      {cards.map((card, idx) => {
        const IconComponent = card.icon;
        return (
          <div key={idx} className="summary-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div>
              <div className="card-top">
                <span className="card-label">{card.label}</span>
                <div className={`card-icon ${card.colorClass}`}>
                  <IconComponent size={20} />
                </div>
              </div>
              <div>
                <div className="card-value">{card.value}</div>
                <div className="card-subtext">{card.subtext}</div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

