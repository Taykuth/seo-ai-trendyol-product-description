import json
import pandas as pd
from sqlalchemy import select
from .db import SessionLocal
from .models import Product

def ingest_csv(csv_path: str) -> int:
    df = pd.read_csv(csv_path)
    required = ["merchant_sku", "title"]
    for c in required:
        if c not in df.columns:
            raise ValueError(f"CSV eksik kolon: {c}")

    count = 0
    with SessionLocal() as db:
        for _, row in df.iterrows():
            sku = str(row["merchant_sku"]).strip()
            title = str(row["title"]).strip()

            barcode = str(row["barcode"]).strip() if "barcode" in df.columns and pd.notna(row.get("barcode")) else None
            brand = str(row["brand"]).strip() if "brand" in df.columns and pd.notna(row.get("brand")) else None
            cat = str(row["category_path"]).strip() if "category_path" in df.columns and pd.notna(row.get("category_path")) else None
            old = str(row["old_description"]) if "old_description" in df.columns and pd.notna(row.get("old_description")) else None
            src = str(row["source_url"]).strip() if "source_url" in df.columns and pd.notna(row.get("source_url")) else None

            image_urls = None
            if "image_urls" in df.columns and pd.notna(row.get("image_urls")):
                raw = str(row["image_urls"]).strip()
                if raw.startswith("["):
                    image_urls = raw
                else:
                    image_urls = json.dumps([u.strip() for u in raw.split("|") if u.strip()], ensure_ascii=False)

            existing = db.execute(select(Product).where(Product.merchant_sku == sku)).scalar_one_or_none()
            if existing:
                existing.title = title
                existing.barcode = barcode
                existing.brand = brand
                existing.category_path = cat
                existing.old_description = old
                existing.source_url = src
                existing.image_urls_json = image_urls
            else:
                p = Product(
                    merchant_sku=sku,
                    barcode=barcode,
                    title=title,
                    brand=brand,
                    category_path=cat,
                    old_description=old,
                    source_url=src,
                    image_urls_json=image_urls
                )
                db.add(p)
                count += 1

        db.commit()
    return count
