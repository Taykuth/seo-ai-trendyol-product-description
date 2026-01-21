import requests
from requests.auth import HTTPBasicAuth
from config.trendyol_config import API_KEY, API_SECRET, SUPPLIER_ID, BASE_URL


def fetch_all_products():
    all_products = []
    page = 0
    size = 50

    url = f"{BASE_URL}/product/sellers/{SUPPLIER_ID}/products"

    headers = {
        "User-Agent": f"{SUPPLIER_ID} - SelfIntegration",
        "Accept": "application/json"
    }

    while True:
        params = {
            "page": page,
            "size": size,
            "approved": True
        }

        response = requests.get(
            url,
            auth=HTTPBasicAuth(API_KEY, API_SECRET),
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            raise Exception(
                f"API error {response.status_code}: {response.text}"
            )

        data = response.json()
        content = data.get("content", [])

        if not content:
            break

        all_products.extend(content)
        page += 1

    return all_products
