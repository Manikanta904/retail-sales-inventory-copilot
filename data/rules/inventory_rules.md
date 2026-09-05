# Retail Inventory Management Rules

## 1. Stock Coverage & Stock-Out Risk Thresholds
- **Critical Stock-Out Risk (`CRITICAL_STOCK_OUT_RISK`)**: Triggered when `stock_coverage_days < 7.0` days while `current_stock > 0`. Indicates an imminent stock-out prediction before inventory hits zero.
- **Out of Stock (`OUT_OF_STOCK`)**: Triggered when `current_stock == 0`. Immediate inventory depletion.
- **Low Stock Warning (`LOW_STOCK`)**: Triggered when `current_stock <= reorder_point` or `stock_coverage_days < 14.0` days.
- **Normal Inventory (`NORMAL`)**: Triggered when inventory coverage is between 14.0 and 60.0 days and stock is below 2.0x target level.

## 2. Overstock & Slow-Moving Definitions
- **Overstocked (`OVERSTOCKED`)**: Triggered when `current_stock >= target_stock_level * 2.0`. Excess capital tied up in inventory.
- **Slow-Moving (`SLOW_MOVING`)**: Triggered when average daily sales velocity `avg_daily_sales <= 0.25` units/day while holding `current_stock >= 15` units.
- **Overstocked & Slow-Moving (`OVERSTOCKED_SLOW_MOVING`)**: Triggered when both overstock and slow-moving criteria are met simultaneously.

## 3. Zero-Sales Handling & Demand Assumptions
- When `current_stock == 0` and `avg_daily_sales == 0`: `stock_coverage_days = 0.0`, status is `OUT_OF_STOCK`.
- When `current_stock > 0` and `avg_daily_sales == 0`: `stock_coverage_days = float('inf')` (Infinity), status is `SLOW_MOVING` if stock >= 15.
- Demand velocity is calculated over a rolling 30-day window unless otherwise specified.
