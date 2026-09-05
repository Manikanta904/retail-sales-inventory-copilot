"""
FastAPI route handlers for Retail Sales and Inventory Copilot.
Delegates business processing to DataService and AnalyticsService,
and query reasoning to CopilotService.
"""
from typing import List
from fastapi import APIRouter

from backend.models.schemas import (
    ProductResponse,
    StoreResponse,
    DashboardSummaryResponse,
    AttentionSummaryResponse,
    AttentionItemResponse,
    CopilotQueryRequest,
    CopilotQueryResponse,
)
from backend.services.data_service import DataService
from backend.services.analytics import AnalyticsService
from backend.services.retrieval import RuleRetrievalService
from backend.services.gemini_service import GeminiService
from backend.services.copilot import CopilotService

router = APIRouter(prefix="/api", tags=["retail-copilot"])

# Initialize services
data_service = DataService()
analytics_service = AnalyticsService(data_service)
retrieval_service = RuleRetrievalService()
gemini_service = GeminiService()

copilot_service = CopilotService(
    data_service=data_service,
    analytics_service=analytics_service,
    retrieval_service=retrieval_service,
    gemini_service=gemini_service,
)


@router.get("/health")
def health_check():
    """Returns application health status."""
    return {"status": "ok", "message": "Service is healthy"}


@router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard_summary():
    """
    Returns high-level retail dashboard summary metrics derived from deterministic analytics.
    """
    df_sales = data_service.df_sales
    df_stores = data_service.df_stores
    df_products = data_service.df_products

    min_dt, max_dt = data_service.get_date_range()

    # Query analytics service for operational counts
    stockouts = analytics_service.detect_stock_out_risks()
    overstocks = analytics_service.detect_overstock_and_slow_moving()
    trends = analytics_service.detect_sales_spikes_and_drops()

    out_of_stock_count = sum(1 for item in stockouts if item["status"] == "OUT_OF_STOCK")
    critical_risk_count = sum(1 for item in stockouts if item["status"] == "CRITICAL_STOCK_OUT_RISK")
    low_stock_count = sum(1 for item in stockouts if item["status"] == "LOW_STOCK")
    overstocked_count = len(overstocks)
    spikes_count = sum(1 for item in trends if item["event_type"] == "SALES_SPIKE")
    drops_count = sum(1 for item in trends if item["event_type"] == "SALES_DROP")

    return DashboardSummaryResponse(
        total_stores=len(df_stores),
        total_products=len(df_products),
        total_sales_transactions=len(df_sales),
        total_revenue_ytd=round(float(df_sales["total_revenue"].sum()), 2),
        total_units_sold=int(df_sales["units_sold"].sum()),
        out_of_stock_count=out_of_stock_count,
        critical_stock_out_risk_count=critical_risk_count,
        critical_stockouts_count=out_of_stock_count + critical_risk_count,
        low_stock_warnings_count=low_stock_count,
        overstocked_items_count=overstocked_count,
        spikes_detected_count=spikes_count,
        drops_detected_count=drops_count,
        date_range_start=min_dt.strftime("%Y-%m-%d"),
        date_range_end=max_dt.strftime("%Y-%m-%d"),
    )



@router.get("/attention", response_model=AttentionSummaryResponse)
def get_attention_items():
    """
    Returns operational items requiring immediate attention (stock-out risks, overstocks, spikes, drops).
    """
    stockouts = analytics_service.detect_stock_out_risks()
    overstocks = analytics_service.detect_overstock_and_slow_moving()
    trends = analytics_service.detect_sales_spikes_and_drops()

    attention_items: List[AttentionItemResponse] = []

    # Process stock-out risks
    for item in stockouts:
        severity = "HIGH" if item["status"] in ["OUT_OF_STOCK", "CRITICAL_STOCK_OUT_RISK"] else "MEDIUM"
        metric_val = f"Stock: {item['stock_on_hand']} units (Coverage: {item['stock_coverage_days']} days)"
        attention_items.append(
            AttentionItemResponse(
                store_id=item["store_id"],
                store_name=item["store_name"],
                product_id=item["product_id"],
                product_name=item["product_name"],
                category=item["category"],
                issue_type=item["status"],
                severity=severity,
                metric_value=metric_val,
                evidence=item["evidence"],
            )
        )

    # Process overstocks / slow moving
    for item in overstocks:
        severity = "HIGH" if item["status"] == "OVERSTOCKED_SLOW_MOVING" else "MEDIUM"
        metric_val = f"Stock: {item['stock_on_hand']} units (Avg sales: {item['avg_daily_sales']} units/day)"
        attention_items.append(
            AttentionItemResponse(
                store_id=item["store_id"],
                store_name=item["store_name"],
                product_id=item["product_id"],
                product_name=item["product_name"],
                category=item["category"],
                issue_type=item["status"],
                severity=severity,
                metric_value=metric_val,
                evidence=item["evidence"],
            )
        )

    # Process sales spikes and drops
    for item in trends:
        severity = "HIGH" if item["event_type"] == "SALES_SPIKE" else "MEDIUM"
        metric_val = f"Ratio: {item['sales_ratio']}x ({item['percentage_change']}%)"
        attention_items.append(
            AttentionItemResponse(
                store_id=item["store_id"],
                store_name=item["store_name"],
                product_id=item["product_id"],
                product_name=item["product_name"],
                category=item["category"],
                issue_type=item["event_type"],
                severity=severity,
                metric_value=metric_val,
                evidence=item["evidence"],
            )
        )

    high_count = sum(1 for i in attention_items if i.severity == "HIGH")
    medium_count = sum(1 for i in attention_items if i.severity == "MEDIUM")
    low_count = sum(1 for i in attention_items if i.severity == "LOW")

    return AttentionSummaryResponse(
        total_attention_items=len(attention_items),
        high_severity_count=high_count,
        medium_severity_count=medium_count,
        low_severity_count=low_count,
        items=attention_items,
    )


@router.get("/products", response_model=List[ProductResponse])
def get_products():
    """Returns list of products from product catalog."""
    df_products = data_service.df_products
    results = []
    for _, row in df_products.iterrows():
        results.append(
            ProductResponse(
                product_id=row["product_id"],
                product_name=row["product_name"],
                category=row["category"],
                cost_price=float(row["cost_price"]),
                unit_price=float(row["unit_price"]),
                reorder_point=int(row["reorder_point"]),
                target_stock_level=int(row["target_stock_level"]),
            )
        )
    return results


@router.get("/stores", response_model=List[StoreResponse])
def get_stores():
    """Returns list of retail store locations."""
    df_stores = data_service.df_stores
    results = []
    for _, row in df_stores.iterrows():
        results.append(
            StoreResponse(
                store_id=row["store_id"],
                store_name=row["store_name"],
                location=row["location"],
                region=row["region"],
                store_type=row["store_type"],
            )
        )
    return results


@router.post("/copilot/query", response_model=CopilotQueryResponse)
def query_copilot(request: CopilotQueryRequest):
    """
    Executes complete retail copilot orchestration pipeline.
    """
    return copilot_service.process_query(request)
