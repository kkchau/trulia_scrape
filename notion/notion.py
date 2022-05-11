import argparse
import requests
import os
from pathlib import Path

DATABASE_ID = '92ec2168f53d481d81baa34962bb3ea6'

NOTION_BASE_URL = "https://api.notion.com/v1"
AUTH_TOKEN = os.getenv("NOTION_API_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
}

def get_database(database_id: str):
    """Retrieves database response from Notion"""
    print(os.getenv("NOTION_API_TOKEN"))
    print(HEADERS)
    endpoint = f"{NOTION_BASE_URL}/databases/{database_id}"
    response = requests.get(endpoint, headers=HEADERS)
    return response

def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("listings_csv", type=Path)
    return parser

def main():
    """Main entrypoint"""
    args = _get_parser.parse_args()
    # Parse listings
    database_data = get_database(DATABASE_ID)
    return database_data

    # Add listings to data if doesn't exist (key = address)

if __name__ == '__main__':
    main()
