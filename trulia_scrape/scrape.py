import csv
import requests
import json
from pathlib import Path
from typing import Optional, List, Mapping, Union
import sys
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import re
import logging
from trulia_scrape.constants import BASE_URL, QUERY_URL
from trulia_scrape.features import feature_parser

logger = logging.getLogger(__name__)

def get_document(url: str = QUERY_URL):
    """Get HTML document from query url. Returns bs4 html-parsed document"""
    response = requests.get(
      url,
      headers={
            "Content-Type": "text/html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        },
    )
    response.raise_for_status()
    document = BeautifulSoup(response.text, "html.parser")
    return document

def retrieve_listings_links(document: BeautifulSoup):
    """Extract property links from listings from HTML document"""
    listing_links = [
        f"{BASE_URL}{listing['href']}"
        for listing
        in document.find_all(attrs={"data-testid": "property-card-link"}, href=True)
    ]
    return listing_links

def _get_listing_price(document: BeautifulSoup):
    """Get and parse listing price"""
    list_price = float(document.find("h3", attrs={"data-testid": "on-market-price-details"}).text.replace("$", "").replace(",", ""))
    return {"list_price": list_price}

def _get_listing_description(document):
    """Address and text description"""
    property_description = json.loads(
        document.find("script", attrs={"data-testid": "hdp-seo-product-schema"}).text
    )

    return {
        "address": property_description.get("name"),
        "property_description": property_description.get("description")
    }

def _format_listing_features(features: List[str]) -> Mapping[str, Union[str, float, int, List]]:
    """Format list of features to dictionary for ease of use"""
    parsed_features = {"raw_feature_notes": []}
    for raw_feature_string in features:
        parsed_feature = None
        for key, feature_format_fn in feature_parser.items():
            if re.match(key, raw_feature_string):
                parsed_feature = feature_format_fn(raw_feature_string)
        if parsed_feature:
            parsed_features.update(parsed_feature)
        else:
            parsed_features['raw_feature_notes'].append(raw_feature_string)
    parsed_features['raw_feature_notes'] = ';'.join(parsed_features['raw_feature_notes'])
    return parsed_features

def parse_listing(document: BeautifulSoup, link: Optional[str] = None):
    """Parse listing document for features"""

    logger.info(f"Parsing listing {link}")

    # Listing price
    list_price = _get_listing_price(document)

    # Listing description
    listing_description = _get_listing_description(document)

    # Features
    all_features = [feature.text for feature in document.find_all("span", class_ = re.compile(r"Feature__FeatureListItem"))]
    parsed_features = _format_listing_features(all_features)

    features = {}
    features['link'] = link
    features.update(list_price)
    features.update(listing_description)
    features.update(parsed_features)
    return features

def write_listings(listings: List[Mapping]):
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            'address',
            'list_price',
            'beds',
            'baths_full',
            'baths_half',
            'garage_spaces',
            'link',
            'living_area',
            'lot_area',
            'year_built',
            'property_description',
            'raw_feature_notes'
        ]
    )
    writer.writeheader()
    for listing in listings:
        writer.writerow(listing)

def main(document: Optional[Path] = None):
    """Main"""
    search_document = get_document()
    listing_links = retrieve_listings_links(search_document)

    logger.info(f"Got the following links: {listing_links}")

    listing_features = []
    for listing_link in listing_links[:10]:
        try:
            sleep(randint(1,5)) # Workaround bot blocking
            listing_features.append(parse_listing(get_document(listing_link), listing_link))
        except Exception:
            print(listing_link)
            continue
    
    return listing_features

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    listings = main()
    write_listings(listings)

