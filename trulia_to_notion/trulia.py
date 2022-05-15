import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Union

from bs4 import BeautifulSoup

from trulia_to_notion.features import feature_parser
from trulia_to_notion.util import random_request

logger = logging.getLogger(__name__)


class Listing:
    RE_ADDRESS = re.compile(
        r"^(?P<HOUSE_NUMBER>\d+) "
        r"(?P<STREET>[\w\s]+), "
        r"(?P<CITY>[\w\s]+), "
        r"(?P<STATE>\w{2}) "
        r"(?P<ZIP_CODE>\d+)$"
    )

    def __init__(self, document: BeautifulSoup, link: Optional[str] = None):
        self._features = self.parse_listing(document, link)

    @property
    def features(self):
        """Return feature dictionary of Listing"""
        return self._features

    @features.setter
    def features(self, features: Dict):
        self._features = features

    @staticmethod
    def _get_listing_price(document: BeautifulSoup):
        """Get and parse listing price"""
        list_price = float(
            document.find("h3", attrs={"data-testid": "on-market-price-details"})
            .text.replace("$", "")
            .replace(",", "")
        )
        return {"list_price": list_price}

    def _get_listing_description(self, document):
        """Address and text description"""
        property_description = json.loads(
            document.find(
                "script", attrs={"data-testid": "hdp-seo-product-schema"}
            ).text
        )

        # Parse address
        address = property_description.get("name")
        matched_address = self.RE_ADDRESS.match(address).groupdict()

        return {
            "address": address,
            "street_address": f"{matched_address.get('HOUSE_NUMBER', '')} {matched_address.get('STREET', '')}",
            "city": matched_address.get("CITY"),
            "state": matched_address.get("STATE"),
            "zip_code": matched_address.get("ZIP_CODE"),
            "property_description": property_description.get("description"),
        }

    @staticmethod
    def _format_listing_features(
        features: List[str],
    ) -> Mapping[str, Union[str, float, int, List]]:
        """Format list of features to dictionary for ease of use"""
        parsed_features = {"raw_feature_notes": ""}
        raw_feature_notes = []
        for raw_feature_string in features:
            parsed_feature = None
            for key, feature_format_fn in feature_parser.items():
                if re.match(key, raw_feature_string):
                    parsed_feature = feature_format_fn(raw_feature_string)
            if parsed_feature:
                parsed_features.update(parsed_feature)
            else:
                raw_feature_notes.append(raw_feature_string)
        parsed_features["raw_feature_notes"] = ";".join(raw_feature_notes)
        return parsed_features

    def parse_listing(self, document: BeautifulSoup, link: Optional[str] = None):
        """Parse listing document for features"""

        logger.info(f"Parsing listing {link}")

        # Listing price
        list_price = self._get_listing_price(document)

        # Listing description
        listing_description = self._get_listing_description(document)

        # Features
        all_features = [
            feature.text
            for feature in document.find_all(
                "span", class_=re.compile(r"Feature__FeatureListItem")
            )
        ]
        parsed_features = self._format_listing_features(all_features)

        # Default features
        features = {
            "address": "",
            "baths_full": 0,
            "baths_half": 0,
            "beds": 0,
            "garage_spaces": 0,
            "link": "",
            "list_price": 0.0,
            "living_area": 0.0,
            "lot_area": 0.0,
            "property_description": "",
            "raw_feature_notes": "",
            "year_built": 0,
        }
        features["link"] = link
        features.update(list_price)
        features.update(listing_description)
        features.update(parsed_features)
        return features


class TruliaConnection:
    def __init__(self, base_url: str, document: Optional[Path] = None):
        self.base_url = base_url
        self.query_document = document
        self._listings = []

    @property
    def listings(self):
        return self._listings

    @staticmethod
    def get_document(url: str):
        """Get HTML document from query url. Returns bs4 html-parsed document"""
        logger.info(f"Retrieving: {url=}")
        response = random_request(url, "get", delay=True)
        response.raise_for_status()
        document = BeautifulSoup(response.text, "html.parser")
        return document

    @staticmethod
    def retrieve_listings_links(base_url: str, document: BeautifulSoup):
        """Extract property links from listings from HTML document"""
        listing_links = [
            f"{base_url}{listing['href']}"
            for listing in document.find_all(
                attrs={"data-testid": "property-card-link"}, href=True
            )
        ]
        return listing_links

    def get_listings(self, query_url: str, max_listings: int):

        if self.query_document:
            with open(self.query_document, "r") as query_document_fh:
                search_document = BeautifulSoup(query_document_fh, "html.parser")
        else:
            search_document = self.get_document(query_url)

        listing_links = self.retrieve_listings_links(self.base_url, search_document)
        logger.info(f"Got the following links: {listing_links}")
        listings = []
        for listing_link in listing_links[:max_listings]:
            try:
                listings.append(Listing(self.get_document(listing_link), listing_link))
            except Exception:
                logger.error(
                    f"Error retrieving listing information for {listing_link=}"
                )
                continue
        self._listings = listings
        return listings
