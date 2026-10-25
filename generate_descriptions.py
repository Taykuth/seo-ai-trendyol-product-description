"""Step 2: generate new descriptions for the fetched products and write a review sheet.

Usage:
    python generate_descriptions.py --limit 1     # try a single product first
    python generate_descriptions.py               # whole catalog

Nothing is sent back to Trendyol. The output Excel file is reviewed by a person,
who decides which descriptions are uploaded.
"""

import argparse
import time

import pandas as pd

from services.ai_description import generate_with_retry

RAW_PATH = "outputs/products_raw.xlsx"
OUT_PATH = "outputs/products_with_ai.xlsx"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="process only the first N products")
    parser.add_argument("--delay", type=float, default=6.0, help="seconds to wait between API calls")
    args = parser.parse_args()

    df = pd.read_excel(RAW_PATH)
    if args.limit:
        df = df.head(args.limit).copy()

    df["new_description"] = ""
    df["ai_status"] = ""

    for idx, row in df.iterrows():
        text, status = generate_with_retry(row.to_dict())
        df.at[idx, "new_description"] = text
        df.at[idx, "ai_status"] = status
        print(f"{idx + 1}/{len(df)} -> {status}")
        time.sleep(args.delay)  # stay under the OpenAI rate limit

    df.to_excel(OUT_PATH, index=False)
    passed = int((df["ai_status"] == "OK").sum())
    print(f"Done: {passed}/{len(df)} passed the rule checks. Review sheet: {OUT_PATH}")


if __name__ == "__main__":
    main()
