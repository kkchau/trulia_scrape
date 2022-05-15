import json
from random import choice, randint
from time import sleep
from typing import Dict, Optional

import requests

from trulia_to_notion.constants import USER_AGENTS


def random_request(
    request_url: str,
    request_type: str,
    data: Optional[Dict] = None,
    delay: bool = False,
) -> requests.Response:
    """Request utility with rotated/random headers"""

    request_function = {
        "get": requests.get,
        "post": requests.post,
        "patch": requests.patch,
        "delete": requests.delete,
    }

    # Headers with random values
    headers = {"Content-Type": "text/html", "User-Agent": choice(USER_AGENTS)}

    # Optionally sleep before making request to work around rate limiting
    if delay:
        sleep(randint(1, 10))

    if request_type == "get":
        response = request_function[request_type](request_url, headers=headers)
    else:
        response = request_function[request_type](
            request_url, headers=headers, data=json.dumps(data)
        )
    response.raise_for_status()
    return response
