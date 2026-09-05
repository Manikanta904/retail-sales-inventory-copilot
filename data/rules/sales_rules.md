# Retail Sales Performance Rules

## 1. Sales Spike Detection
- **Sales Spike (`SALES_SPIKE`)**: Triggered when the average daily sales velocity in a recent period (e.g. 14 days) is at least `1.8x` (180%) of the historical baseline period (e.g. 30 days) average daily sales velocity.
- Spikes highlight promotional success, seasonal surge, or sudden demand spikes.

## 2. Sales Drop Detection
- **Sales Drop (`SALES_DROP`)**: Triggered when recent average daily sales velocity drops to `0.4x` (40%) or less of the historical baseline period average daily sales velocity.
- Drops indicate demand collapse, unannounced stock depletion, shift in customer preference, or post-promo lull.

## 3. Product Performance & Period Comparisons
- **Period Comparison**: Performance is evaluated by comparing equal-duration consecutive date ranges (e.g., current 30 days vs prior 30 days).
- **Percentage Change**: Calculated as `((current_value - previous_value) / previous_value) * 100`.
- **Baseline Interpretation**: Percentage change is only valid when `previous_value > 0`. If `previous_value == 0`, percentage change is flagged as uncalculated to avoid division by zero.
