"""Parse Trulia query and add to Notion database"""
import argparse
import logging
from pathlib import Path

from trulia_to_notion.constants import (
    NOTION_BASE_URL,
    NOTION_DATABASE_ID,
    TRULIA_BASE_URL,
    TRULIA_QUERY_ENDPOINT,
)
from trulia_to_notion.notion import NotionRealEstateDB
from trulia_to_notion.trulia import TruliaConnection

logger = logging.getLogger(__name__)


def _get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--document",
        help="Path to input Trulia query HTML document (for offline testing)",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--max-listings",
        "-n",
        help="Maximum number of listings to analyze",
        type=int,
        default=10,
    )
    return parser


def main():
    """Main entrypoint"""
    args = _get_parser().parse_args()

    # Generate list of latest listings
    trulia = TruliaConnection(TRULIA_BASE_URL, document=args.document)
    listings = trulia.get_listings(
        query_url=f"{TRULIA_BASE_URL}/{TRULIA_QUERY_ENDPOINT}",
        max_listings=args.max_listings,
    )

    # Initiate connection to Notion
    notion = NotionRealEstateDB(NOTION_BASE_URL, NOTION_DATABASE_ID)

    for listing in listings:
        notion.add_listing(listing)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
