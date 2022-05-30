"""Parse Trulia query and add to Notion database"""
import argparse
import logging
import pickle
from pathlib import Path

from trulia_to_notion.classify import classify, push_classifications
from trulia_to_notion.constants import (
    NOTION_BASE_URL,
    NOTION_DATABASE_ID,
    TRULIA_BASE_URL,
    TRULIA_QUERY_ENDPOINT,
)
from trulia_to_notion.notion import NotionRealEstateDB
from trulia_to_notion.train import train_classifier
from trulia_to_notion.trulia import TruliaConnection

logger = logging.getLogger(__name__)


def _get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Get listings
    get_listings_cmd = subparsers.add_parser("get-listings")
    get_listings_cmd.add_argument(
        "--document",
        help="Path to input Trulia query HTML document (for offline testing)",
        type=Path,
        default=None,
    )
    get_listings_cmd.add_argument(
        "--max-listings",
        "-n",
        help="Maximum number of listings to analyze",
        type=int,
        default=10,
    )
    get_listings_cmd.set_defaults(func=_get_listings)

    # Train classifier
    train_classifier_cmd = subparsers.add_parser("train-classifier")
    train_classifier_cmd.add_argument(
        "--output",
        help="Path to output file for model",
        type=Path,
        default="model.pickle",
    )
    train_classifier_cmd.set_defaults(func=_train_classifier)

    # Classify listings
    classify_listings_cmd = subparsers.add_parser("classify-listings")
    classify_listings_cmd.add_argument(
        "--model-path",
        help="Path to model pickle file",
        type=Path,
        default="model.pickle",
    )
    classify_listings_cmd.add_argument(
        "--output",
        help="Path to output CSV for classified listings",
        type=Path,
        default=None,
    )
    classify_listings_cmd.set_defaults(func=_classify_listings)

    return parser


def _get_listings(args):
    """Generate list of latest listings from Trulia and add to Notion database"""
    # Generate list of latest listings
    trulia = TruliaConnection(TRULIA_BASE_URL, document=args.document)
    listings = trulia.get_listings(
        query_url=f"{TRULIA_BASE_URL}/{TRULIA_QUERY_ENDPOINT}",
        max_listings=args.max_listings,
    )

    # Add listings to database
    notion = NotionRealEstateDB(NOTION_BASE_URL, NOTION_DATABASE_ID)
    for listing in listings:
        notion.add_listing(listing)


def _train_classifier(args):
    """Train and write to disk a logistic regression model"""
    notion = NotionRealEstateDB(NOTION_BASE_URL, NOTION_DATABASE_ID)
    model_info = train_classifier(notion.get_pages())

    # Write model to disk
    with open(args.output, "wb") as pickle_fh:
        pickle.dump(model_info["model"], pickle_fh)


def _classify_listings(args):
    """Predict suitable listings and mark on database"""
    notion = NotionRealEstateDB(NOTION_BASE_URL, NOTION_DATABASE_ID)

    # Load model
    with open(args.model_path, "rb") as model_fh:
        model = pickle.load(model_fh)
    classified_listings = classify(notion.get_pages(), model)
    push_classifications(classified_listings, notion)


def main():
    """Main entrypoint"""
    args = _get_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    main()
