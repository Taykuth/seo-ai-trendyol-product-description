import time
import os
import pandas as pd
from services.trendyol_api import fetch_all_products

def normalize(products):
    rows = []

    for p in products:
        rows.append({
            "barcode": p.get("barcode"),
            "title": p.get("title"),
            "description": p.get("description"),
            "brand": p.get("brand"),
            "category": p.get("categoryName")
        })

    return rows

if __name__ == "__main__":
    products = fetch_all_products()
    rows = normalize(products)

    df = pd.DataFrame(rows)
    df.to_excel("outputs/products_raw.xlsx", index=False)

    print(f"{len(df)} ürün Excel'e yazıldı")
import pandas as pd
from services.ai_description import generate_description

if __name__ == "__main__":
    df = pd.read_excel("outputs/products_raw.xlsx")

    # TEK ÜRÜN (örnek: ilk satır)
    row = df.iloc[0].to_dict()

    new_desc = generate_description(row)
    df.loc[0, "new_description"] = new_desc

    df.to_excel("outputs/products_with_ai_test.xlsx", index=False)
    print("Tek ürün için new_description yazıldı.")
import pandas as pd
from services.ai_description import generate_with_retry

if __name__ == "__main__":
    df = pd.read_excel("outputs/products_raw.xlsx")

    if "new_description" not in df.columns:
        df["new_description"] = ""
    if "ai_status" not in df.columns:
        df["ai_status"] = ""

    for idx, row in df.iterrows():
        product = row.to_dict()

        new_desc, status = generate_with_retry(product)
        df.at[idx, "new_description"] = new_desc
        df.at[idx, "ai_status"] = status

        print(f"{idx+1}/{len(df)} -> {status}")

        time.sleep(6)   # <-- TAM OLARAK BURAYA
                        #     (for döngüsünün EN SON SATIRI)

    df.to_excel("outputs/products_with_ai.xlsx", index=False)
    print("Batch tamamlandı: outputs/products_with_ai.xlsx")


