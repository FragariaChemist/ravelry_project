from pathlib import Path
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"


# Load Ravelry API credentials from .env
load_dotenv()

USERNAME = os.getenv("ravname")
PASSWORD = os.getenv("password")


SEARCH_URL = "https://api.ravelry.com/patterns/search.json"
DETAIL_URL = "https://api.ravelry.com/patterns.json"


def get_auth():
    """Create Ravelry API authentication."""

    if not USERNAME or not PASSWORD:
        raise ValueError(
            "Ravelry API credentials were not found. "
            "Make sure ravname and password are set in your .env file."
        )

    return HTTPBasicAuth(USERNAME, PASSWORD)


def unique_pattern_collection(category, total):
    """
    Collect unique Ravelry patterns from a pattern category.

    Parameters
    ----------
    category : str
        Ravelry pattern category, such as "socks" or "pullover".
    total : int
        Number of unique patterns to collect.

    Returns
    -------
    pandas.DataFrame
        Pattern ID, name, and photo URL.
    """

    auth = get_auth()

    page = 1
    page_size = 150

    posts = []
    unique_ids = set()

    while len(unique_ids) < total:

        params = {
            "page_size": page_size,
            "craft": "knitting",
            "pc": category,
            "availability": "-discontinued",
            "language": "en",
            "photo": "yes",
            "country": "united-states",
            "sort": "popularity",
            "page": page,
        }

        response = requests.get(
            SEARCH_URL,
            params=params,
            auth=auth,
            timeout=30,
        )

        response.raise_for_status()

        rav_data = response.json()
        patterns = rav_data.get("patterns", [])

        if not patterns:
            break

        for pattern in patterns:

            pattern_id = pattern["id"]

            if pattern_id not in unique_ids:
                unique_ids.add(pattern_id)
                posts.append(pattern)

            if len(unique_ids) >= total:
                break

        print(
            f"Collected {len(unique_ids)} "
            f"of {total} patterns..."
        )

        page += 1

    pattern_ids = [
        post["id"]
        for post in posts
    ]

    names = [
        post["name"]
        for post in posts
    ]

    photos = [
        post["first_photo"]["medium_url"]
        if post.get("first_photo")
        and post["first_photo"].get("medium_url")
        else "No photo"
        for post in posts
    ]

    patterns_df = pd.DataFrame(
        {
            "id": pattern_ids,
            "name": names,
            "photo": photos,
        }
    )

    print(
        f"Total unique pattern IDs collected: "
        f"{len(patterns_df)}"
    )

    return patterns_df


def detail_collector(patterns):
    """
    Collect detailed information for Ravelry patterns.

    Parameters
    ----------
    patterns : pandas.DataFrame
        DataFrame containing a column named "id".

    Returns
    -------
    pandas.DataFrame
        Detailed pattern information used by the project.
    """

    auth = get_auth()

    pattern_ids = patterns["id"].tolist()
    raw_details = []

    for number, pattern_id in enumerate(
        pattern_ids,
        start=1,
    ):

        params = {
            "ids": pattern_id,
        }

        response = requests.get(
            DETAIL_URL,
            params=params,
            auth=auth,
            timeout=30,
        )

        response.raise_for_status()

        pattern_data = response.json()

        pattern_detail = pattern_data.get(
            "patterns",
            {},
        ).get(
            str(pattern_id)
        )

        if pattern_detail is not None:
            raw_details.append(pattern_detail)

        print(
            f"Collected details for "
            f"{number} of {len(pattern_ids)} patterns..."
        )

    detail_rows = []

    for pattern in raw_details:

        yarn_weight = pattern.get("yarn_weight")

        if yarn_weight:
            yarn_weight_name = yarn_weight.get(
                "name",
                "Unavailable",
            )
        else:
            yarn_weight_name = "Unavailable"

        pattern_author = pattern.get(
            "pattern_author",
            {},
        )

        difficulty = pattern.get(
            "difficulty_average"
        )

        rating = pattern.get(
            "rating_average"
        )

        detail_rows.append(
            {
                "id": pattern.get("id"),
                "name": pattern.get("name"),
                "author": pattern_author.get("name"),
                "difficulty_avg": (
                    round(difficulty, 2)
                    if difficulty is not None
                    else None
                ),
                "gauge": pattern.get("gauge"),
                "gauge_divisor": pattern.get(
                    "gauge_divisor"
                ),
                "gauge_pattern": pattern.get(
                    "gauge_pattern"
                ),
                "max_yardage": pattern.get(
                    "yardage_max"
                ),
                "notes": pattern.get("notes"),
                "price": pattern.get("price"),
                "projects_count": pattern.get(
                    "projects_count"
                ),
                "queued_projects_count": pattern.get(
                    "queued_projects_count"
                ),
                "rating_avg": (
                    round(rating, 2)
                    if rating is not None
                    else None
                ),
                "sizes_available": pattern.get(
                    "sizes_available"
                ),
                "yarn_weight": yarn_weight_name,
                "permalink": pattern.get(
                    "permalink"
                ),
            }
        )

    return pd.DataFrame(detail_rows)


def data_collection_pipeline(category, total):
    """
    Search Ravelry, collect pattern details, and save them.

    Parameters
    ----------
    category : str
        Ravelry pattern category.
    total : int
        Number of patterns to collect.

    Returns
    -------
    pandas.DataFrame
        Detailed pattern data.
    """

    print(
        f"Searching for {total} "
        f"{category} patterns..."
    )

    patterns = unique_pattern_collection(
        category,
        total,
    )

    print("Collecting pattern details...")

    details = detail_collector(patterns)

    DATA_DIR.mkdir(exist_ok=True)

    output_path = (
        DATA_DIR
        / f"{category}_details.csv"
    )

    details.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved {len(details)} patterns to:"
    )

    print(output_path)

    return details


if __name__ == "__main__":

    # Small test run.
    # We will change this after verifying the API code works.
    data_collection_pipeline(
        category="scarf",
        total=5,
    )