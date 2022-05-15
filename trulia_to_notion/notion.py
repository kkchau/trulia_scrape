import json
import logging
from typing import Dict, Optional, Sequence, Union

import requests

from trulia_to_notion.constants import NOTION_HEADERS
from trulia_to_notion.trulia import Listing

logger = logging.getLogger(__name__)


FIELD_MAPS = {"address": "Address"}


def _rich_text_property(content: str):
    return {"rich_text": [{"text": {"content": content}}]}


def _url_property(content: str):
    return {"url": content}


def _numeric_property(content: Union[int, float]):
    return {"number": content}


class NotionRealEstateDB:
    def __init__(self, base_url: str, database_id: str):
        self.base_url = base_url
        self.database_id = database_id

        self.database_url = f"{self.base_url}/databases/{self.database_id}"
        self.page_url = f"{self.base_url}/pages"
        self.block_url = f"{self.base_url}/blocks"

        # Check database connection
        self.get_database()

    def get_database(self):
        """Retrieves database response from Notion"""
        endpoint = f"{self.base_url}/databases/{self.database_id}"
        response = requests.get(endpoint, headers=NOTION_HEADERS)
        return response

    @staticmethod
    def _paragraph_block(content: str):
        return {
            "type": "paragraph",
            "paragraph": _rich_text_property(content),
        }

    @staticmethod
    def _bulleted_list_block(content: Sequence[str]):
        """Assumes content is delimited by ';'"""
        item_list = [
            {"type": "paragraph", "paragraph": _rich_text_property(value)}
            for value in content
        ]
        return {
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [],
                "children": item_list,
            },
        }

    def _make_listing_payload(self, features: Dict):
        """
        Create page creation payload

        Properties:
            Address
            Listing Price
            Link
            Beds
            Baths
            Garage Spaces
            Size
            Lot Size
            Year Built

        Blocks:
            Description
            Raw Notes
        """

        # Properties
        properties = {
            "Link": _url_property(features["link"]),
            "Address": _rich_text_property(features["address"]),
            "Listing Price": _numeric_property(features["list_price"]),
            "Beds": _numeric_property(features["beds"]),
            "Baths": _numeric_property(
                float(features["baths_full"]) + (float(features["baths_half"]) * 0.5)
            ),
            "Garage Spaces": _numeric_property(int(features["garage_spaces"])),
            "Size (sq. ft.)": _numeric_property(float(features["living_area"])),
            "Lot Size (sq. ft.)": _numeric_property(float(features["lot_area"])),
            "Year Built": _numeric_property(int(features["year_built"])),
        }

        # Child blocks
        children = [
            dict(
                {"object": "block"},
                **self._paragraph_block(features["property_description"]),
            ),
            dict(
                {"object": "block"},
                **self._bulleted_list_block(
                    features["raw_feature_notes"].strip().split(";")
                ),
            ),
        ]
        return {
            "properties": properties,
            "children": children,
        }

    def _get_existing_listing(self, address: str) -> Optional[str]:
        """Check that listing exists in database"""
        response = requests.post(
            f"{self.database_url}/query",
            data=json.dumps(
                {
                    "filter": {
                        "property": "Address",
                        "rich_text": {"equals": address},
                    }
                }
            ),
            headers=NOTION_HEADERS,
        )
        results = response.json()["results"]
        if results:
            return results[0]["id"]
        return None

    def _update_existing_listing(self, listing_features: Dict, page_id: str):

        # Make update payload
        payload = self._make_listing_payload(listing_features)
        payload_properties = payload["properties"]
        payload_children = payload["children"]
        for block in payload_children:
            del block["object"]
            del block["type"]

        logger.info("Updating page properties")
        response = requests.patch(
            f"{self.page_url}/{page_id}",
            headers=NOTION_HEADERS,
            data=json.dumps({"properties": payload_properties}),
        )

        logger.info("Deleting child blocks")
        child_blocks = requests.get(
            f"{self.block_url}/{page_id}/children", headers=NOTION_HEADERS
        ).json()["results"]
        for block_id in [block["id"] for block in child_blocks]:
            requests.delete(f"{self.block_url}/{block_id}", headers=NOTION_HEADERS)

        logger.info("Adding updated child blocks")
        requests.patch(
            f"{self.block_url}/{page_id}/children",
            headers=NOTION_HEADERS,
            data=json.dumps({"children": payload_children}),
        )
        return response

    def _add_new_listing(self, listing_features: Dict):
        payload = self._make_listing_payload(listing_features)
        payload["parent"] = {"database_id": self.database_id}
        response = requests.post(
            f"{self.page_url}", headers=NOTION_HEADERS, data=json.dumps(payload)
        )
        return response

    def add_listing(self, listing: Listing):
        """
        Adds a listing to the database. If the listing exists, updates that listing
        """
        existing_listing = self._get_existing_listing(listing.features["address"])
        if existing_listing:
            logger.info(f"Found existing listing with page id {existing_listing}")
            response = self._update_existing_listing(listing.features, existing_listing)
        else:
            logger.info(f"Creating new listing for {listing.features['link']}")
            response = self._add_new_listing(listing.features)
