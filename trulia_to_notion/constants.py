import os

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
]

# Trulia
TRULIA_BASE_URL = "https://www.trulia.com"
TRULIA_QUERY_ENDPOINT = "for_sale/37.31454,37.52585,-122.12055,-121.7992_xy/3p_beds/2p_baths/800000-1500000_price/1000p_sqft/SINGLE-FAMILY_HOME_type/date;d_sort/0.0459p_ls/0-200_hoa/12_zm/"
SCRAPE_HEADERS = {
    "Content-Type": "text/html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
}

# Notion
NOTION_BASE_URL = "https://api.notion.com/v1"
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Notion-Version": "2022-02-22",
}

NOTION_DATABASE_ID = "92ec2168f53d481d81baa34962bb3ea6"

# ML
FEATURES = (
    "Listing Price",
    "Beds",
    "Baths",
    "Garage Spaces",
    "Size (sq. ft.)",
    "Lot Size (sq. ft.)",
    "Zip Code",
)
SELECTOR_FIELD = "Like"
PREDICTOR_FIELD = "Prediction"
