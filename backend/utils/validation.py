"""
Validation utilities for retail copilot queries, dates, stores, and products.
Ensures invalid or ungrounded input is rejected cleanly before reaching reasoning logic.
"""
import re
from dataclasses import dataclass
from typing import List, Optional
import pandas as pd

from backend.core.config import MAX_QUESTION_LENGTH
from backend.models.schemas import CopilotQueryRequest
from backend.services.data_service import DataService


@dataclass
class ValidationResult:
    is_valid: bool
    error_message: Optional[str] = None
    insufficient_data: bool = False
    missing_information: Optional[List[str]] = None
    available_information: Optional[List[str]] = None


def validate_date_string(date_str: str) -> bool:
    """Validates if a string is formatted as YYYY-MM-DD."""
    try:
        pd.to_datetime(date_str, format="%Y-%m-%d", errors="raise")
        return True
    except Exception:
        return False


def validate_copilot_query(
    request: CopilotQueryRequest, data_service: DataService
) -> ValidationResult:
    """
    Validates a CopilotQueryRequest against input constraints, date formats,
    and dataset store/product catalogs. Rejects invalid queries deterministically.
    """
    raw_question = request.question or ""
    cleaned_question = raw_question.strip()

    # 1. Empty or whitespace-only question validation
    if not cleaned_question:
        return ValidationResult(
            is_valid=False,
            error_message="Please provide a retail question.",
            insufficient_data=True,
            missing_information=["Valid non-empty retail query string"],
            available_information=[
                "Ask about stock-out risks, low-stock items, sales spikes, or store performance."
            ],
        )

    # 2. Excessively long question validation
    if len(cleaned_question) > MAX_QUESTION_LENGTH:
        return ValidationResult(
            is_valid=False,
            error_message=f"Question is too long (max {MAX_QUESTION_LENGTH} characters).",
            insufficient_data=False,
        )

    # 3. Date format and range validation
    if request.start_date:
        if not validate_date_string(request.start_date):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid start date format. Expected YYYY-MM-DD.",
            )
    if request.end_date:
        if not validate_date_string(request.end_date):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid end date format. Expected YYYY-MM-DD.",
            )
    if request.start_date and request.end_date:
        if pd.to_datetime(request.start_date) > pd.to_datetime(request.end_date):
            return ValidationResult(
                is_valid=False,
                error_message="Invalid date range: start date cannot be after end date.",
            )

    # 4. Explicit Store ID Validation
    df_stores = data_service.df_stores
    valid_store_ids = set(df_stores["store_id"].values) if not df_stores.empty else set()

    if request.store_id:
        if request.store_id not in valid_store_ids:
            return ValidationResult(
                is_valid=False,
                error_message="No matching store found.",
                insufficient_data=True,
                missing_information=[f"Store '{request.store_id}' in catalog"],
                available_information=[f"Available stores: {', '.join(sorted(valid_store_ids))}"],
            )

    # Check store ID patterns inside text (e.g. STR999)
    text_store_matches = re.findall(r"\bSTR\d+\b", cleaned_question, re.IGNORECASE)
    for s_match in text_store_matches:
        s_upper = s_match.upper()
        if s_upper not in valid_store_ids:
            return ValidationResult(
                is_valid=False,
                error_message="No matching store found.",
                insufficient_data=True,
                missing_information=[f"Store '{s_upper}' in catalog"],
                available_information=[f"Available stores: {', '.join(sorted(valid_store_ids))}"],
            )

    # 5. Explicit Product ID Validation
    df_products = data_service.df_products
    valid_prod_ids = set(df_products["product_id"].values) if not df_products.empty else set()

    if request.product_id:
        if request.product_id not in valid_prod_ids:
            return ValidationResult(
                is_valid=False,
                error_message="No matching product found.",
                insufficient_data=True,
                missing_information=[f"Product '{request.product_id}' in catalog"],
                available_information=[f"Catalog contains {len(valid_prod_ids)} products."],
            )

    # Check product ID patterns inside text (e.g. PRD999)
    text_prod_matches = re.findall(r"\bPRD\d+\b", cleaned_question, re.IGNORECASE)
    for p_match in text_prod_matches:
        p_upper = p_match.upper()
        if p_upper not in valid_prod_ids:
            return ValidationResult(
                is_valid=False,
                error_message="No matching product found.",
                insufficient_data=True,
                missing_information=[f"Product '{p_upper}' in catalog"],
                available_information=[
                    f"Available product IDs range from PRD001 to PRD{len(valid_prod_ids):03d}."
                ],
            )

    # 6. Unknown Specific Product/Entity Detection in Query Text
    raw_words = cleaned_question.split()
    words = [re.sub(r"[^\w]", "", w) for w in raw_words]
    stop_words = {
        "what", "where", "which", "who", "how", "why", "tell", "me", "my", "i", "your", "our", "us",
        "about", "show", "is", "are", "was", "were", "the", "a", "an", "for", "in", "of", "to", "and", "or",
        "this", "that", "these", "those", "any", "all", "products", "items", "store", "stores", "sales", "inventory",
        "stock", "out", "low", "many", "units", "sold", "give", "details", "information", "data", "list",
        "get", "find", "search", "likely", "run", "top", "best", "worst", "high", "low", "most", "least",
        "trending", "recent", "arent", "did", "does", "do", "cause", "caused", "increase", "increased", "fall", "fell",
        "have", "has", "had", "having", "there", "we", "be", "been", "being", "can", "could", "would", "should"
    }


    # Extract non-stop words
    query_tokens = [w.lower() for w in words if w.lower() not in stop_words and len(w) > 0]


    if query_tokens:
        catalog_text = (
            " "
            + " ".join(df_products["product_name"].astype(str)).lower()
            + " "
            + " ".join(df_products["category"].astype(str)).lower()
            + " "
            + " ".join(df_products["product_id"].astype(str)).lower()
        )
        
        # Tokenize catalog into discrete word set
        catalog_tokens = set(re.findall(r"\b\w+\b", catalog_text))

        # Generic domain terms that can appear in broad analytical questions
        generic_domain_terms = {
            "performance", "perform", "performing", "revenue", "demand", "month", "week", "today", "year",
            "slow", "moving", "slow-moving", "stagnant", "spike", "spikes", "surge", "surges", "drop", "drops",
            "risk", "overstock", "overstocked", "overstocking", "surplus", "understock", "reorder",
            "category", "categories", "pricing", "margin", "trend", "trends", "stockout", "stock-out",
            "stockouts", "stock-outs", "depletion", "selling", "sales", "sold", "attention", "urgent",
            "priority", "issue", "issues", "problem", "problems", "needs", "item", "items", "product", "products",
            "store", "stores", "location", "locations", "unusual", "abnormal", "anomaly", "anomalies",
            "significant", "unprecedented", "well", "good", "bad", "situation", "status", "summary",
            "overview", "condition", "state", "competitor", "competitors", "promotion", "promotions",
            "advertising", "demographics"
        }




        # Non-generic tokens are specific product names / entities (e.g. "playstation", "xbox", "mouse", "coffee")
        specific_entity_tokens = [k for k in query_tokens if k not in generic_domain_terms]

        if specific_entity_tokens:
            matching_tokens = [k for k in specific_entity_tokens if k in catalog_tokens]

            # If query contains specific product entity names (e.g., "playstation") but NONE exist in catalog
            if not matching_tokens:
                return ValidationResult(
                    is_valid=False,
                    error_message="No matching product found.",
                    insufficient_data=True,
                    missing_information=[f"Requested product ('{cleaned_question}') in catalog"],
                    available_information=[
                        "Catalog includes Electronics, Home & Kitchen, Office Supplies, Groceries, and Apparel."
                    ],
                )

    return ValidationResult(is_valid=True)
