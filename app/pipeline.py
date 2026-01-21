import argparse
from .ingest import ingest_csv
from .run_batch import run_batch

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/input_products.csv")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    n = ingest_csv(args.csv)
    print({"ingested": n})

    r = run_batch(limit=args.limit, force=args.force)
    print(r)

if __name__ == "__main__":
    main()
