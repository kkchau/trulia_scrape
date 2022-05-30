"""Classiifcation of Trulia listings"""
import json
import logging
from typing import Dict

import pandas as pd
import requests
from notion import NotionRealEstateDB
from sklearn.linear_model import LogisticRegression

from trulia_to_notion.constants import FEATURES, NOTION_HEADERS

logger = logging.getLogger(__name__)


def classify(data: pd.DataFrame, model: LogisticRegression) -> Dict[str, bool]:
    """Classify listings data using the passed logistic regression model

    :param data: DataFrame of features
    :param model: LogisticRegression model

    :return DataFrame of addresses mapped to predictions
    """
    x = data.copy()  # pylint: disable=C0103
    x.set_index("Address", inplace=True)

    logger.info("Predicting listings")
    x.loc[:, "Prediction"] = model.predict(x.loc[:, FEATURES])

    predicted_listings = {
        address: prediction["Prediction"]
        for address, prediction in x[["Prediction"]].to_dict("index").items()
    }
    return predicted_listings


def push_classifications(
    classified_listings: Dict[str, bool], notion: NotionRealEstateDB
):
    """
    Push classification results to remote Notion database

    :param classified_listings: DataFrame of predicted listings
    """
    logger.info("Pushing listings to Notion")
    for address, prediction in classified_listings.items():
        page = notion.get_existing_listing(address)
        if page:
            response = requests.patch(
                f"{notion.page_url}/{page}",
                headers=NOTION_HEADERS,
                data=json.dumps(
                    {"properties": {"Prediction": {"checkbox": prediction}}}
                ),
            )
            response.raise_for_status()
