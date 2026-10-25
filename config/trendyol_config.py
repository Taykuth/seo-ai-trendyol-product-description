import os

from dotenv import load_dotenv

load_dotenv()

# Credentials come from the environment (.env), never from source code.
API_KEY = os.getenv("TRENDYOL_API_KEY", "")
API_SECRET = os.getenv("TRENDYOL_API_SECRET", "")
SUPPLIER_ID = os.getenv("TRENDYOL_SUPPLIER_ID", "")
BASE_URL = os.getenv("TRENDYOL_BASE_URL", "https://apigw.trendyol.com/integration")


def require_credentials() -> None:
    missing = [
        name
        for name, value in (
            ("TRENDYOL_API_KEY", API_KEY),
            ("TRENDYOL_API_SECRET", API_SECRET),
            ("TRENDYOL_SUPPLIER_ID", SUPPLIER_ID),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Missing environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill them in."
        )
