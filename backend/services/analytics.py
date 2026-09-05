"""
Deterministic Analytics Service for Retail Sales and Inventory Copilot.
Implements stock coverage calculations, inventory risk detection, trend analysis,
product performance summaries, and store sales performance reporting.
"""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from backend.core.config import (
    CRITICAL_STOCK_DAYS_THRESHOLD,
    LOW_STOCK_COVERAGE_DAYS_THRESHOLD,
    OVERSTOCK_MULTIPLIER_THRESHOLD,
    SLOW_MOVING_DAILY_SALES_THRESHOLD,
    SLOW_MOVING_MIN_STOCK,
    SPIKE_RATIO_THRESHOLD,
    DROP_RATIO_THRESHOLD,
    DEFAULT_RECENT_PERIOD_DAYS,
    DEFAULT_BASELINE_PERIOD_DAYS,
)
from backend.services.data_service import DataService


class AnalyticsService:
    """
    Service providing deterministic analytics for inventory management and sales analytics.
    Every finding includes underlying numerical evidence and safe zero-division handling.
    """

    def __init__(self, data_service: DataService) -> None:
        self.data_service = data_service

    @staticmethod
    def calculate_stock_coverage(current_stock: float, avg_daily_sales: float) -> float:
        """
        Calculates stock coverage days = current_stock / avg_daily_sales.

        Handles zero-sales cases cleanly:
        - current_stock == 0 and average_daily_sales == 0 -> stock_coverage_days = 0.0 (OUT_OF_STOCK)
        - current_stock > 0 and average_daily_sales == 0 -> stock_coverage_days = float('inf') (Infinity coverage)
        """
        if avg_daily_sales <= 0:
            return float("inf") if current_stock > 0 else 0.0
        return round(float(current_stock) / float(avg_daily_sales), 2)


    @staticmethod
    def calculate_percentage_change(current: float, previous: float) -> Optional[float]:
        """
        Calculates percentage change = ((current - previous) / previous) * 100.
        Returns None if previous is zero or invalid to prevent division-by-zero.
        """
        if previous is None or previous == 0:
            return None
        return round(((current - previous) / previous) * 100.0, 2)

    def detect_stock_out_risks(
        self,
        as_of_date: Optional[str | pd.Timestamp] = None,
        lookback_days: int = 30,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Identifies products at risk of stock-out based on current stock levels,
        reorder thresholds, and average daily sales over a lookback window.
        """
        if as_of_date is None:
            _, max_dt = self.data_service.get_date_range()
            as_of_dt = max_dt
        else:
            as_of_dt = pd.to_datetime(as_of_date)

        start_dt = as_of_dt - pd.Timedelta(days=lookback_days - 1)

        # Get latest inventory snapshot up to as_of_date
        df_inv = self.data_service.get_latest_inventory_snapshot(
            as_of_date=as_of_dt, store_id=store_id, product_id=product_id
        )
        if df_inv.empty:
            return []

        # Get sales within lookback period
        df_sales = self.data_service.get_sales_df(
            start_date=start_dt, end_date=as_of_dt, store_id=store_id, product_id=product_id
        )

        # Pre-aggregate sales sums per store_id and product_id for fast lookup
        sales_sums = (
            df_sales.groupby(["store_id", "product_id"])["units_sold"].sum().to_dict()
        )

        df_products = self.data_service.df_products
        df_stores = self.data_service.df_stores

        results: List[Dict[str, Any]] = []

        for _, inv_row in df_inv.iterrows():
            s_id = inv_row["store_id"]
            p_id = inv_row["product_id"]
            stock = float(inv_row["stock_on_hand"])

            p_match = df_products[df_products["product_id"] == p_id]
            s_match = df_stores[df_stores["store_id"] == s_id]
            if p_match.empty or s_match.empty:
                continue

            p_info = p_match.iloc[0]
            s_info = s_match.iloc[0]

            # Fast vectorized sales sum lookup
            total_units_sold = float(sales_sums.get((s_id, p_id), 0.0))
            avg_daily_sales = total_units_sold / float(lookback_days)

            coverage_days = self.calculate_stock_coverage(stock, avg_daily_sales)
            reorder_pt = float(p_info["reorder_point"])

            is_out_of_stock = stock == 0
            is_critical = stock > 0 and coverage_days < CRITICAL_STOCK_DAYS_THRESHOLD
            is_low_stock = stock > 0 and not is_critical and stock <= reorder_pt

            if is_out_of_stock or is_critical or is_low_stock:
                if is_out_of_stock:
                    status = "OUT_OF_STOCK"
                    evidence_prefix = "OUT OF STOCK"
                elif is_critical:
                    status = "CRITICAL_STOCK_OUT_RISK"
                    evidence_prefix = "PREDICTED STOCK-OUT RISK"
                else:
                    status = "LOW_STOCK"
                    evidence_prefix = "LOW STOCK WARNING"

                coverage_str = (
                    "0.00 days" if is_out_of_stock else ("Infinity" if coverage_days == float("inf") else f"{coverage_days:.2f} days")
                )

                evidence = (
                    f"{evidence_prefix} - Store {s_id} ({s_info['store_name']}), Product {p_id} ({p_info['product_name']}): "
                    f"Current stock is {int(stock)} units (Reorder Point: {int(reorder_pt)}). "
                    f"Avg daily sales over past {lookback_days} days ({start_dt.strftime('%Y-%m-%d')} to {as_of_dt.strftime('%Y-%m-%d')}) "
                    f"is {avg_daily_sales:.2f} units/day. Stock coverage is {coverage_str} "
                    f"(Critical threshold: < {CRITICAL_STOCK_DAYS_THRESHOLD} days)."
                )

                results.append({
                    "store_id": s_id,
                    "store_name": s_info["store_name"],
                    "product_id": p_id,
                    "product_name": p_info["product_name"],
                    "category": p_info["category"],
                    "stock_on_hand": int(stock),
                    "reorder_point": int(reorder_pt),
                    "target_stock_level": int(p_info["target_stock_level"]),
                    "avg_daily_sales": round(avg_daily_sales, 2),
                    "stock_coverage_days": coverage_days if coverage_days != float("inf") else 999.0,
                    "status": status,
                    "evidence": evidence,
                })


        return sorted(results, key=lambda x: (x["stock_on_hand"], x["stock_coverage_days"]))

    def detect_overstock_and_slow_moving(
        self,
        as_of_date: Optional[str | pd.Timestamp] = None,
        lookback_days: int = 30,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detects slow-moving products and overstocked inventory as of as_of_date.
        """
        if as_of_date is None:
            _, max_dt = self.data_service.get_date_range()
            as_of_dt = max_dt
        else:
            as_of_dt = pd.to_datetime(as_of_date)

        start_dt = as_of_dt - pd.Timedelta(days=lookback_days - 1)

        df_inv = self.data_service.get_latest_inventory_snapshot(
            as_of_date=as_of_dt, store_id=store_id, product_id=product_id
        )
        if df_inv.empty:
            return []

        df_sales = self.data_service.get_sales_df(
            start_date=start_dt, end_date=as_of_dt, store_id=store_id, product_id=product_id
        )

        # Pre-aggregate sales sums per store_id and product_id for fast lookup
        sales_sums = (
            df_sales.groupby(["store_id", "product_id"])["units_sold"].sum().to_dict()
        )

        df_products = self.data_service.df_products
        df_stores = self.data_service.df_stores

        results: List[Dict[str, Any]] = []

        for _, inv_row in df_inv.iterrows():
            s_id = inv_row["store_id"]
            p_id = inv_row["product_id"]
            stock = float(inv_row["stock_on_hand"])

            p_match = df_products[df_products["product_id"] == p_id]
            s_match = df_stores[df_stores["store_id"] == s_id]
            if p_match.empty or s_match.empty:
                continue

            p_info = p_match.iloc[0]
            s_info = s_match.iloc[0]

            # Fast vectorized sales sum lookup
            total_units_sold = float(sales_sums.get((s_id, p_id), 0.0))
            avg_daily_sales = total_units_sold / float(lookback_days)

            coverage_days = self.calculate_stock_coverage(stock, avg_daily_sales)
            target_stock = float(p_info["target_stock_level"])

            is_overstocked = stock >= (target_stock * OVERSTOCK_MULTIPLIER_THRESHOLD)
            is_slow_moving = (
                avg_daily_sales <= SLOW_MOVING_DAILY_SALES_THRESHOLD
                and stock >= SLOW_MOVING_MIN_STOCK
            )

            if is_overstocked or is_slow_moving:
                if is_overstocked and is_slow_moving:
                    status = "OVERSTOCKED_SLOW_MOVING"
                elif is_overstocked:
                    status = "OVERSTOCKED"
                else:
                    status = "SLOW_MOVING"

                coverage_str = (
                    "Infinity" if coverage_days == float("inf") else f"{coverage_days:.2f} days"
                )

                evidence = (
                    f"Store {s_id} ({s_info['store_name']}), Product {p_id} ({p_info['product_name']}): "
                    f"Current stock is {int(stock)} units (Target stock: {int(target_stock)}). "
                    f"Avg daily sales over past {lookback_days} days is {avg_daily_sales:.2f} units/day. "
                    f"Stock coverage is {coverage_str}. "
                    f"Status triggered because stock is {stock/target_stock:.2f}x of target level "
                    f"and avg daily sales is {avg_daily_sales:.2f} units/day."
                )

                results.append({
                    "store_id": s_id,
                    "store_name": s_info["store_name"],
                    "product_id": p_id,
                    "product_name": p_info["product_name"],
                    "category": p_info["category"],
                    "stock_on_hand": int(stock),
                    "target_stock_level": int(target_stock),
                    "avg_daily_sales": round(avg_daily_sales, 2),
                    "stock_coverage_days": coverage_days if coverage_days != float("inf") else 999.0,
                    "status": status,
                    "evidence": evidence,
                })

        return sorted(results, key=lambda x: x["stock_on_hand"], reverse=True)

    def detect_sales_spikes_and_drops(
        self,
        end_date: Optional[str | pd.Timestamp] = None,
        recent_days: int = DEFAULT_RECENT_PERIOD_DAYS,
        baseline_days: int = DEFAULT_BASELINE_PERIOD_DAYS,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detects significant sales spikes and drops by comparing a recent period against a historical baseline.
        If end_date is None, uses fast vectorized pandas rolling windows across the dataset timeline.
        """
        min_dt, max_dt = self.data_service.get_date_range()

        df_sales = self.data_service.df_sales
        df_products = self.data_service.df_products
        df_stores = self.data_service.df_stores

        stores = df_stores[df_stores["store_id"] == store_id] if store_id else df_stores
        products = df_products[df_products["product_id"] == product_id] if product_id else df_products

        store_map = dict(zip(df_stores["store_id"], df_stores["store_name"]))
        prod_info = {r["product_id"]: (r["product_name"], r["category"]) for _, r in df_products.iterrows()}

        if end_date is not None:
            eval_dates = [pd.to_datetime(end_date)]
        else:
            min_eval_dt = min_dt + pd.Timedelta(days=recent_days + baseline_days - 1)
            eval_dates = pd.date_range(min_eval_dt, max_dt) if min_eval_dt <= max_dt else [max_dt]

        # Filter sales dataframe to relevant stores and products
        s_ids = set(stores["store_id"])
        p_ids = set(products["product_id"])
        sub_sales = df_sales[(df_sales["store_id"].isin(s_ids)) & (df_sales["product_id"].isin(p_ids))]

        # Reindex to full daily grid per store & product for accurate rolling calculations
        idx = pd.MultiIndex.from_product(
            [pd.date_range(min_dt, max_dt), sorted(list(s_ids)), sorted(list(p_ids))],
            names=["date", "store_id", "product_id"]
        )

        grouped = sub_sales.groupby(["date", "store_id", "product_id"])["units_sold"].sum().reindex(idx, fill_value=0).reset_index()
        grouped = grouped.sort_values(["store_id", "product_id", "date"])

        # Calculate rolling 14-day recent sum and shifted 30-day baseline sum
        grouped["recent_units"] = grouped.groupby(["store_id", "product_id"])["units_sold"].transform(
            lambda x: x.rolling(recent_days, min_periods=recent_days).sum()
        )
        grouped["baseline_units"] = grouped.groupby(["store_id", "product_id"])["units_sold"].transform(
            lambda x: x.shift(recent_days).rolling(baseline_days, min_periods=baseline_days).sum()
        )

        # Filter to requested evaluation dates
        eval_mask = grouped["date"].isin(eval_dates) & grouped["recent_units"].notna() & grouped["baseline_units"].notna()
        valid = grouped[eval_mask].copy()

        if valid.empty:
            return []

        valid["recent_avg"] = valid["recent_units"] / float(recent_days)
        valid["baseline_avg"] = valid["baseline_units"] / float(baseline_days)

        valid["ratio"] = np.where(
            valid["baseline_avg"] > 0,
            valid["recent_avg"] / valid["baseline_avg"],
            np.where(valid["recent_avg"] > 0, np.inf, 1.0)
        )

        valid["is_spike"] = (
            ((valid["ratio"] >= SPIKE_RATIO_THRESHOLD) & (valid["recent_units"] >= 5))
            | ((valid["baseline_avg"] == 0) & (valid["recent_avg"] >= 1.5))
        )
        valid["is_drop"] = (valid["ratio"] <= DROP_RATIO_THRESHOLD) & (valid["baseline_units"] >= 10)

        # Deduplicate peak events per (store_id, product_id, event_type)
        peak_events: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

        for _, r in valid[valid["is_spike"] | valid["is_drop"]].iterrows():
            event_type = "SALES_SPIKE" if r["is_spike"] else "SALES_DROP"
            s_id = r["store_id"]
            p_id = r["product_id"]
            s_name = store_map.get(s_id, s_id)
            p_name, category = prod_info.get(p_id, (p_id, "General"))

            recent_start_dt = r["date"] - pd.Timedelta(days=recent_days - 1)
            baseline_end_dt = recent_start_dt - pd.Timedelta(days=1)
            baseline_start_dt = baseline_end_dt - pd.Timedelta(days=baseline_days - 1)

            pct_change = (
                self.calculate_percentage_change(r["recent_avg"], r["baseline_avg"])
                if r["baseline_avg"] > 0
                else (999.0 if event_type == "SALES_SPIKE" else -100.0)
            )

            evidence = (
                f"Store {s_id} ({s_name}), Product {p_id} ({p_name}): "
                f"{event_type} detected! Recent period ({recent_start_dt.strftime('%Y-%m-%d')} to {r['date'].strftime('%Y-%m-%d')}) "
                f"avg daily sales: {r['recent_avg']:.2f} units/day (Total: {int(r['recent_units'])} units). "
                f"Baseline period ({baseline_start_dt.strftime('%Y-%m-%d')} to {baseline_end_dt.strftime('%Y-%m-%d')}) "
                f"avg daily sales: {r['baseline_avg']:.2f} units/day (Total: {int(r['baseline_units'])} units). "
                f"Ratio: {r['ratio']:.2f}x (Percentage change: {pct_change}%)."
            )

            event_data = {
                "store_id": s_id,
                "store_name": s_name,
                "product_id": p_id,
                "product_name": p_name,
                "category": category,
                "event_type": event_type,
                "recent_avg_daily_sales": round(r["recent_avg"], 2),
                "baseline_avg_daily_sales": round(r["baseline_avg"], 2),
                "sales_ratio": round(r["ratio"], 2) if r["ratio"] != float("inf") else 999.0,
                "percentage_change": pct_change,
                "recent_units_sold": int(r["recent_units"]),
                "baseline_units_sold": int(r["baseline_units"]),
                "evidence": evidence,
            }

            key = (s_id, p_id, event_type)
            if key not in peak_events:
                peak_events[key] = event_data
            else:
                if event_type == "SALES_SPIKE" and r["ratio"] > peak_events[key]["sales_ratio"]:
                    peak_events[key] = event_data
                elif event_type == "SALES_DROP" and r["ratio"] < peak_events[key]["sales_ratio"]:
                    peak_events[key] = event_data

        results = list(peak_events.values())
        return sorted(results, key=lambda x: abs(x["percentage_change"] or 0), reverse=True)



    def get_product_performance(
        self,
        start_date: Optional[str | pd.Timestamp] = None,
        end_date: Optional[str | pd.Timestamp] = None,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
        compare_previous: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Calculates detailed product sales performance for a configurable date range.
        Optionally compares against the preceding equal-length date window.
        """
        min_dt, max_dt = self.data_service.get_date_range()
        end_dt = pd.to_datetime(end_date) if end_date else max_dt
        start_dt = pd.to_datetime(start_date) if start_date else (end_dt - pd.Timedelta(days=29))

        num_days = max(1, (end_dt - start_dt).days + 1)

        df_sales = self.data_service.get_sales_df(
            start_date=start_dt, end_date=end_dt, store_id=store_id, product_id=product_id
        )

        # Previous period comparison setup
        prev_end_dt = start_dt - pd.Timedelta(days=1)
        prev_start_dt = prev_end_dt - pd.Timedelta(days=num_days - 1)
        df_prev_sales = pd.DataFrame()
        if compare_previous:
            df_prev_sales = self.data_service.get_sales_df(
                start_date=prev_start_dt, end_date=prev_end_dt, store_id=store_id, product_id=product_id
            )

        products = self.data_service.df_products
        if product_id:
            products = products[products["product_id"] == product_id]

        results: List[Dict[str, Any]] = []

        for _, p_info in products.iterrows():
            pid = p_info["product_id"]
            curr_p_sales = df_sales[df_sales["product_id"] == pid] if not df_sales.empty else pd.DataFrame()

            units_sold = int(curr_p_sales["units_sold"].sum()) if not curr_p_sales.empty else 0
            revenue = round(float(curr_p_sales["total_revenue"].sum()), 2) if not curr_p_sales.empty else 0.0
            avg_daily_sales = round(units_sold / float(num_days), 2)

            prev_units_sold = None
            prev_revenue = None
            units_change_pct = None
            revenue_change_pct = None

            if compare_previous:
                prev_p_sales = df_prev_sales[df_prev_sales["product_id"] == pid] if not df_prev_sales.empty else pd.DataFrame()
                prev_units_sold = int(prev_p_sales["units_sold"].sum()) if not prev_p_sales.empty else 0
                prev_revenue = round(float(prev_p_sales["total_revenue"].sum()), 2) if not prev_p_sales.empty else 0.0

                units_change_pct = self.calculate_percentage_change(units_sold, prev_units_sold)
                revenue_change_pct = self.calculate_percentage_change(revenue, prev_revenue)

            evidence = (
                f"Product {pid} ({p_info['product_name']}): Sold {units_sold} units for ${revenue:,.2f} revenue "
                f"across {num_days} days ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}). "
                f"Avg daily sales: {avg_daily_sales} units/day. "
            )
            if compare_previous:
                prev_str = f"{prev_units_sold} units / ${prev_revenue:,.2f} revenue" if prev_units_sold is not None else "N/A"
                change_str = f"Units change: {units_change_pct}%, Revenue change: {revenue_change_pct}%" if units_change_pct is not None else "No prior baseline"
                evidence += f"Prior period ({prev_start_dt.strftime('%Y-%m-%d')} to {prev_end_dt.strftime('%Y-%m-%d')}): {prev_str}. {change_str}."

            results.append({
                "product_id": pid,
                "product_name": p_info["product_name"],
                "category": p_info["category"],
                "unit_price": float(p_info["unit_price"]),
                "units_sold": units_sold,
                "revenue": revenue,
                "avg_daily_sales": avg_daily_sales,
                "prev_units_sold": prev_units_sold,
                "prev_revenue": prev_revenue,
                "units_change_pct": units_change_pct,
                "revenue_change_pct": revenue_change_pct,
                "evidence": evidence,
            })

        return sorted(results, key=lambda x: x["revenue"], reverse=True)

    def get_store_sales_summary(
        self,
        start_date: Optional[str | pd.Timestamp] = None,
        end_date: Optional[str | pd.Timestamp] = None,
        compare_previous: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Provides store-level sales performance summaries for a configurable date range.
        """
        min_dt, max_dt = self.data_service.get_date_range()
        end_dt = pd.to_datetime(end_date) if end_date else max_dt
        start_dt = pd.to_datetime(start_date) if start_date else (end_dt - pd.Timedelta(days=29))

        num_days = max(1, (end_dt - start_dt).days + 1)

        df_sales = self.data_service.get_sales_df(start_date=start_dt, end_date=end_dt)

        prev_end_dt = start_dt - pd.Timedelta(days=1)
        prev_start_dt = prev_end_dt - pd.Timedelta(days=num_days - 1)
        df_prev_sales = pd.DataFrame()
        if compare_previous:
            df_prev_sales = self.data_service.get_sales_df(start_date=prev_start_dt, end_date=prev_end_dt)

        stores = self.data_service.df_stores
        products = self.data_service.df_products

        results: List[Dict[str, Any]] = []

        for _, s_info in stores.iterrows():
            sid = s_info["store_id"]
            s_sales = df_sales[df_sales["store_id"] == sid] if not df_sales.empty else pd.DataFrame()

            units_sold = int(s_sales["units_sold"].sum()) if not s_sales.empty else 0
            total_revenue = round(float(s_sales["total_revenue"].sum()), 2) if not s_sales.empty else 0.0
            avg_daily_revenue = round(total_revenue / float(num_days), 2)

            # Top selling product in this store
            top_prod_id = "N/A"
            top_prod_name = "N/A"
            top_prod_rev = 0.0
            if not s_sales.empty:
                top_p_grp = s_sales.groupby("product_id")["total_revenue"].sum().reset_index()
                top_p_row = top_p_grp.sort_values("total_revenue", ascending=False).iloc[0]
                top_prod_id = top_p_row["product_id"]
                top_prod_rev = round(float(top_p_row["total_revenue"]), 2)
                p_match = products[products["product_id"] == top_prod_id]
                if not p_match.empty:
                    top_prod_name = p_match.iloc[0]["product_name"]

            prev_revenue = None
            prev_units = None
            revenue_change_pct = None

            if compare_previous:
                s_prev_sales = df_prev_sales[df_prev_sales["store_id"] == sid] if not df_prev_sales.empty else pd.DataFrame()
                prev_units = int(s_prev_sales["units_sold"].sum()) if not s_prev_sales.empty else 0
                prev_revenue = round(float(s_prev_sales["total_revenue"].sum()), 2) if not s_prev_sales.empty else 0.0
                revenue_change_pct = self.calculate_percentage_change(total_revenue, prev_revenue)

            evidence = (
                f"Store {sid} ({s_info['store_name']}): Total Revenue: ${total_revenue:,.2f}, Total Units: {units_sold} "
                f"over {num_days} days ({start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}). "
                f"Avg Daily Revenue: ${avg_daily_revenue:,.2f}/day. Top Product: {top_prod_id} ({top_prod_name}) "
                f"generating ${top_prod_rev:,.2f}. "
            )
            if compare_previous and prev_revenue is not None:
                evidence += f"Prior period revenue: ${prev_revenue:,.2f} (Revenue change: {revenue_change_pct}%)."

            results.append({
                "store_id": sid,
                "store_name": s_info["store_name"],
                "location": s_info["location"],
                "units_sold": units_sold,
                "total_revenue": total_revenue,
                "avg_daily_revenue": avg_daily_revenue,
                "prev_units_sold": prev_units,
                "prev_total_revenue": prev_revenue,
                "revenue_change_pct": revenue_change_pct,
                "top_selling_product_id": top_prod_id,
                "top_selling_product_name": top_prod_name,
                "top_product_revenue": top_prod_rev,
                "evidence": evidence,
            })

        return sorted(results, key=lambda x: x["total_revenue"], reverse=True)
