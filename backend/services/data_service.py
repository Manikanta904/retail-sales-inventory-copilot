"""
Data loading and query service for Retail Sales and Inventory Copilot.
Loads and cleans stores, products, sales, and inventory datasets using Pandas.
"""
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

from backend.core.config import (
    STORES_CSV_PATH,
    PRODUCTS_CSV_PATH,
    SALES_CSV_PATH,
    INVENTORY_CSV_PATH,
)


class DataService:
    """
    Service responsible for loading, storing, and querying retail CSV datasets.
    """

    def __init__(
        self,
        stores_path: Path = STORES_CSV_PATH,
        products_path: Path = PRODUCTS_CSV_PATH,
        sales_path: Path = SALES_CSV_PATH,
        inventory_path: Path = INVENTORY_CSV_PATH,
    ) -> None:
        self.stores_path = stores_path
        self.products_path = products_path
        self.sales_path = sales_path
        self.inventory_path = inventory_path

        self.df_stores: pd.DataFrame = pd.DataFrame()
        self.df_products: pd.DataFrame = pd.DataFrame()
        self.df_sales: pd.DataFrame = pd.DataFrame()
        self.df_inventory: pd.DataFrame = pd.DataFrame()

        self.load_data()

    def load_data(self) -> None:
        """Loads and pre-processes CSV datasets into pandas DataFrames."""
        if not self.stores_path.exists():
            raise FileNotFoundError(f"Stores dataset missing at {self.stores_path}")
        if not self.products_path.exists():
            raise FileNotFoundError(f"Products dataset missing at {self.products_path}")
        if not self.sales_path.exists():
            raise FileNotFoundError(f"Sales dataset missing at {self.sales_path}")
        if not self.inventory_path.exists():
            raise FileNotFoundError(f"Inventory dataset missing at {self.inventory_path}")

        self.df_stores = pd.read_csv(self.stores_path)
        self.df_products = pd.read_csv(self.products_path)

        self.df_sales = pd.read_csv(self.sales_path)
        self.df_sales["date"] = pd.to_datetime(self.df_sales["date"])
        self.df_sales["units_sold"] = self.df_sales["units_sold"].astype(int)
        self.df_sales["unit_price"] = self.df_sales["unit_price"].astype(float)
        self.df_sales["total_revenue"] = self.df_sales["total_revenue"].astype(float)

        self.df_inventory = pd.read_csv(self.inventory_path)
        self.df_inventory["date"] = pd.to_datetime(self.df_inventory["date"])
        self.df_inventory["stock_on_hand"] = self.df_inventory["stock_on_hand"].astype(int)

    def get_date_range(self) -> Tuple[pd.Timestamp, pd.Timestamp]:
        """Returns the minimum and maximum dates present across sales and inventory datasets."""
        min_sales_date = self.df_sales["date"].min()
        max_sales_date = self.df_sales["date"].max()
        min_inv_date = self.df_inventory["date"].min()
        max_inv_date = self.df_inventory["date"].max()

        min_date = min(min_sales_date, min_inv_date)
        max_date = max(max_sales_date, max_inv_date)
        return min_date, max_date

    def get_sales_df(
        self,
        start_date: Optional[str | pd.Timestamp] = None,
        end_date: Optional[str | pd.Timestamp] = None,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> pd.DataFrame:
        """Filters sales DataFrame based on optional start_date, end_date, store_id, and product_id."""
        df = self.df_sales.copy()
        if start_date is not None:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date is not None:
            df = df[df["date"] <= pd.to_datetime(end_date)]
        if store_id is not None:
            df = df[df["store_id"] == store_id]
        if product_id is not None:
            df = df[df["product_id"] == product_id]
        return df

    def get_inventory_df(
        self,
        start_date: Optional[str | pd.Timestamp] = None,
        end_date: Optional[str | pd.Timestamp] = None,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> pd.DataFrame:
        """Filters inventory DataFrame based on optional start_date, end_date, store_id, and product_id."""
        df = self.df_inventory.copy()
        if start_date is not None:
            df = df[df["date"] >= pd.to_datetime(start_date)]
        if end_date is not None:
            df = df[df["date"] <= pd.to_datetime(end_date)]
        if store_id is not None:
            df = df[df["store_id"] == store_id]
        if product_id is not None:
            df = df[df["product_id"] == product_id]
        return df

    def get_latest_inventory_snapshot(
        self,
        as_of_date: Optional[str | pd.Timestamp] = None,
        store_id: Optional[str] = None,
        product_id: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Gets the latest inventory record for each store and product up to as_of_date.
        If as_of_date is None, uses the maximum date available in the inventory dataset.
        """
        df = self.df_inventory.copy()
        if as_of_date is not None:
            as_of_dt = pd.to_datetime(as_of_date)
            df = df[df["date"] <= as_of_dt]
        if store_id is not None:
            df = df[df["store_id"] == store_id]
        if product_id is not None:
            df = df[df["product_id"] == product_id]

        if df.empty:
            return pd.DataFrame(columns=self.df_inventory.columns)

        # Sort chronologically, group by store_id and product_id, and take the last record
        df = df.sort_values("date").groupby(["store_id", "product_id"], as_index=False).last()
        return df
