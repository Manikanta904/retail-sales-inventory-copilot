"""
Configuration settings and centralized thresholds for Retail Sales and Inventory Copilot.
"""
import os
from pathlib import Path

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Automatically load local .env file into os.environ if present
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val


# Dataset paths
STORES_CSV_PATH = DATA_DIR / "stores.csv"
PRODUCTS_CSV_PATH = DATA_DIR / "products.csv"
SALES_CSV_PATH = DATA_DIR / "sales.csv"
INVENTORY_CSV_PATH = DATA_DIR / "inventory.csv"

# Analytics Thresholds
# Stock Coverage & Risk
CRITICAL_STOCK_DAYS_THRESHOLD = 7.0  # Stock coverage < 7 days indicates critical stock-out risk
LOW_STOCK_COVERAGE_DAYS_THRESHOLD = 14.0  # Stock coverage < 14 days indicates low stock warning

# Overstock & Slow-Moving
OVERSTOCK_MULTIPLIER_THRESHOLD = 2.0  # Current stock >= target_stock * 2.0 indicates overstock
SLOW_MOVING_DAILY_SALES_THRESHOLD = 0.25  # Avg daily sales <= 0.25 units/day indicates slow-moving item
SLOW_MOVING_MIN_STOCK = 15  # Minimum stock required to qualify as overstocked slow-mover

# Trend Analysis (Spikes & Drops)
SPIKE_RATIO_THRESHOLD = 1.8  # Recent daily sales >= 1.8x baseline daily sales indicates a spike
DROP_RATIO_THRESHOLD = 0.4  # Recent daily sales <= 0.4x baseline daily sales indicates a drop
DEFAULT_RECENT_PERIOD_DAYS = 14  # Default duration for recent window
DEFAULT_BASELINE_PERIOD_DAYS = 30  # Default duration for historical baseline comparison window

# Query & Validation Limits
MAX_QUESTION_LENGTH = 500  # Maximum character length for copilot natural language query

# Official Hackathon Compliant Models
GEMINI_LLM_MODEL = "gemini-3.5-flash-lite"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"

