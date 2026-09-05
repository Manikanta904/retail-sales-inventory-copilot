"""
Pydantic schemas for request and response validation across the Retail Copilot API.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


# ---------------------------------------------------------
# Product & Store Schemas
# ---------------------------------------------------------
class ProductResponse(BaseModel):
    product_id: str = Field(..., description="Unique product ID (e.g. PRD001)")
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    cost_price: float = Field(..., description="Unit cost price in USD")
    unit_price: float = Field(..., description="Unit selling price in USD")
    reorder_point: int = Field(..., description="Inventory level triggering reorder")
    target_stock_level: int = Field(..., description="Optimal target stock level")


class StoreResponse(BaseModel):
    store_id: str = Field(..., description="Unique store ID (e.g. STR001)")
    store_name: str = Field(..., description="Store name")
    location: str = Field(..., description="City and state location")
    region: str = Field(..., description="Geographic region")
    store_type: str = Field(..., description="Store format type")


# ---------------------------------------------------------
# Dashboard & Attention Item Schemas
# ---------------------------------------------------------
class DashboardSummaryResponse(BaseModel):
    total_stores: int = Field(..., description="Total active stores")
    total_products: int = Field(..., description="Total active products")
    total_sales_transactions: int = Field(..., description="Total sales transaction count")
    total_revenue_ytd: float = Field(..., description="Total revenue over dataset timeframe")
    total_units_sold: int = Field(..., description="Total units sold across dataset")
    out_of_stock_count: int = Field(..., description="Count of currently depleted items (stock == 0)")
    critical_stock_out_risk_count: int = Field(..., description="Count of items at predicted stock-out risk (stock > 0, coverage < 7.0 days)")
    critical_stockouts_count: int = Field(..., description="Combined total of out-of-stock and critical stock-out risk items")
    low_stock_warnings_count: int = Field(..., description="Count of low-stock items")
    overstocked_items_count: int = Field(..., description="Count of overstocked items")
    spikes_detected_count: int = Field(..., description="Count of recent sales spikes")
    drops_detected_count: int = Field(..., description="Count of recent sales drops")
    date_range_start: str = Field(..., description="Start date of dataset")
    date_range_end: str = Field(..., description="End date of dataset")



class AttentionItemResponse(BaseModel):
    store_id: str = Field(..., description="Store identifier")
    store_name: str = Field(..., description="Store name")
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    issue_type: str = Field(..., description="Issue classification (e.g. OUT_OF_STOCK, LOW_STOCK, OVERSTOCKED, SALES_SPIKE, SALES_DROP)")
    severity: str = Field(..., description="Severity level: HIGH, MEDIUM, LOW")
    metric_value: str = Field(..., description="Primary metric value")
    evidence: str = Field(..., description="Numerical evidence supporting the issue")


class AttentionSummaryResponse(BaseModel):
    total_attention_items: int = Field(..., description="Total attention items count")
    high_severity_count: int = Field(..., description="Count of HIGH severity items")
    medium_severity_count: int = Field(..., description="Count of MEDIUM severity items")
    low_severity_count: int = Field(..., description="Count of LOW severity items")
    items: List[AttentionItemResponse] = Field(default_factory=list, description="List of attention items")


# ---------------------------------------------------------
# Copilot Query & Response Schemas
# ---------------------------------------------------------
class CopilotQueryRequest(BaseModel):
    question: str = Field(..., description="Natural language retail query")
    store_id: Optional[str] = Field(None, description="Optional store filter")
    product_id: Optional[str] = Field(None, description="Optional product filter")
    start_date: Optional[str] = Field(None, description="Optional start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Optional end date (YYYY-MM-DD)")


class EvidenceItem(BaseModel):
    source: str = Field(..., description="Dataset or analysis source")
    metric: str = Field(..., description="Name of the metric evaluated")
    value: str = Field(..., description="Calculated metric value")
    details: str = Field(..., description="Detailed context or observation")


class AssumptionItem(BaseModel):
    statement: str = Field(..., description="Assumption made for analysis")
    basis: str = Field(..., description="Reasoning or constraint behind the assumption")


class RecommendationItem(BaseModel):
    action: str = Field(..., description="Recommended action")
    priority: str = Field(..., description="Priority: HIGH, MEDIUM, LOW")
    expected_impact: str = Field(..., description="Expected business impact")


class CopilotQueryResponse(BaseModel):
    status: str = Field("success", description="Status string: success or insufficient_data")
    answer: str = Field(..., description="Direct answer to the query")
    findings: List[str] = Field(default_factory=list, description="Key analytical findings")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Structured numerical evidence")
    assumptions: List[AssumptionItem] = Field(default_factory=list, description="Assumptions made")
    recommendations: List[RecommendationItem] = Field(default_factory=list, description="Actionable recommendations")
    data_sources: List[str] = Field(default_factory=list, description="Data files/tables queried")
    data_sufficient: bool = Field(True, description="Flag indicating if data was sufficient")


class InsufficientDataResponse(BaseModel):
    status: str = Field("insufficient_data", description="Status indicator")
    answer: str = Field(..., description="Explanation of why data is insufficient")
    missing_information: List[str] = Field(default_factory=list, description="List of missing data elements")
    available_information: List[str] = Field(default_factory=list, description="List of available data elements that could be queried")
