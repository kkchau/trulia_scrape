"""Model training"""
import logging

import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from trulia_to_notion.constants import FEATURES, SELECTOR_FIELD

logger = logging.getLogger(__name__)


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
