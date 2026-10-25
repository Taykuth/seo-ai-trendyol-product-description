"""Step 1: fetch approved products from the Trendyol Seller API and save them to Excel."""

import os

import pandas as pd

from services.trendyol_api import fetch_all_products

RAW_PATH = "outputs/products_raw.xlsx"


def normalize(products: list[dict]) -> list[dict]:
    return [
        {
            "barcode": p.get("barcode"),
            "title": p.get("title"),
            "description": p.get("description"),
            "brand": p.get("brand"),
            "category": p.get("categoryName"),
        }
        for p in products
    ]


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    df = pd.DataFrame(normalize(fetch_all_products()))
    df.to_excel(RAW_PATH, index=False)
    print(f"{len(df)} products written to {RAW_PATH}")
