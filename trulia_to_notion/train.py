import logging
from typing import Dict

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from trulia_to_notion.constants import NOTION_BASE_URL, NOTION_DATABASE_ID
from trulia_to_notion.notion import NotionRealEstateDB

logger = logging.getLogger(__name__)

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


def _parse_properties(properties: Dict):
    return {
        "Listing Price": properties["Listing Price"]["number"],
        "Beds": properties["Beds"]["number"],
        "Baths": properties["Baths"]["number"],
        "Garage Spaces": properties["Garage Spaces"]["number"],
        "Size (sq. ft.)": properties["Size (sq. ft.)"]["number"],
        "Lot Size (sq. ft.)": properties["Lot Size (sq. ft.)"]["number"],
        "Zip Code": properties["Zip Code"]["number"],
        "Like": properties["Like"]["checkbox"],
    }


def train_classifier(input_data: pd.DataFrame):
    """Train classifier with input data"""
    x = input_data.loc[:, FEATURES]  # pylint: disable=C0103
    y = input_data.loc[:, SELECTOR_FIELD]  # pylint: disable=C0103
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.25, random_state=0
    )

    model = LogisticRegression()
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)

    model_info = {
        "model": model,
        "accuracy": metrics.accuracy_score(y_test, y_pred),
        "precision": metrics.precision_score(y_test, y_pred),
        "recall": metrics.recall_score(y_test, y_pred),
        "confusion_matrix": str(metrics.confusion_matrix(y_test, y_pred)),
    }
    logger.info(model_info)
    return model_info


def _get_data(notion_base_url: str, notion_database_id: str):
    notion = NotionRealEstateDB(
        base_url=notion_base_url, database_id=notion_database_id
    )
    pages_properties = [
        _parse_properties(page.get("properties"))
        for page in notion.get_pages().json().get("results")
    ]
    return pages_properties


def train_on_remote_data(notion_base_url: str, notion_database_id: str):
    """Pull data from Notion and train a classifier"""
    data = pd.DataFrame(
        _get_data(
            notion_base_url=notion_base_url, notion_database_id=notion_database_id
        )
    )
    model_info = train_classifier(data)
    return model_info
