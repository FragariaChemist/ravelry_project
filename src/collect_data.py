from pathlib import Path
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
REFRESH_DIR = DATA_DIR / "refresh"


# --------------------------------------------------
# Ravelry API credentials
# --------------------------------------------------

# Load the .env file from the project root.
load_dotenv(PROJECT_DIR / ".env")

USERNAME = os.getenv("ravname")
PASSWORD = os.getenv("password")


# --------------------------------------------------
# Ravelry API endpoints
# --------------------------------------------------

SEARCH_URL = "https://api.ravelry.com/patterns/search.json"
DETAIL_URL = "https://api.ravelry.com/patterns.json"


# --------------------------------------------------
# Pattern categories used by the recommender
# --------------------------------------------------

PATTERN_CATEGORIES = {
    "beanie-toque": 5000,
    "mid-calf": 5000,
    "pullover": 5000,
}


def get_auth():
    """Create Ravelry API authentication."""

    if not USERNAME or not PASSWORD:
        raise ValueError(
            "Ravelry API credentials were not found. "
            "Make sure ravname and password are set "
            "in your .env file."
        )

    return HTTPBasicAuth(
        USERNAME,
        PASSWORD,
    )


def unique_pattern_collection(category, total):
    """
    Collect unique Ravelry patterns from a pattern category.

    Parameters
    ----------
    category : str
        Ravelry pattern category, such as
        "beanie-toque", "mid-calf", or "pullover".
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

        patterns = rav_data.get(
            "patterns",
            [],
        )

        # Stop if Ravelry returns no more patterns.
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

    Pattern IDs are requested in batches of 100
    instead of making one API request per pattern.

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

    batch_size = 100
    raw_details = []

    for start in range(
        0,
        len(pattern_ids),
        batch_size,
    ):

        batch_ids = pattern_ids[
            start:start + batch_size
        ]

        # Ravelry expects multiple IDs separated
        # by literal plus signs.
        id_string = "+".join(
            str(pattern_id)
            for pattern_id in batch_ids
        )

        detail_url = (
            f"{DETAIL_URL}?ids={id_string}"
        )

        response = requests.get(
            detail_url,
            auth=auth,
            timeout=30,
        )

        response.raise_for_status()

        pattern_data = response.json()

        returned_patterns = pattern_data.get(
            "patterns",
            {},
        )

        for pattern_id in batch_ids:

            pattern_detail = returned_patterns.get(
                str(pattern_id)
            )

            if pattern_detail is not None:
                raw_details.append(
                    pattern_detail
                )

        # Do not silently continue if Ravelry
        # returns fewer patterns than requested.
        if len(returned_patterns) != len(batch_ids):
            raise ValueError(
                f"Requested {len(batch_ids)} pattern details "
                f"but Ravelry returned "
                f"{len(returned_patterns)}."
            )

        print(
            f"Collected details for "
            f"{min(start + batch_size, len(pattern_ids))} "
            f"of {len(pattern_ids)} patterns..."
        )

    detail_rows = []

    for pattern in raw_details:

        yarn_weight = pattern.get(
            "yarn_weight"
        )

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
                "author": pattern_author.get(
                    "name"
                ),
                "difficulty_avg": (
                    round(difficulty, 2)
                    if difficulty is not None
                    else None
                ),
                "gauge": pattern.get(
                    "gauge"
                ),
                "gauge_divisor": pattern.get(
                    "gauge_divisor"
                ),
                "gauge_pattern": pattern.get(
                    "gauge_pattern"
                ),
                "max_yardage": pattern.get(
                    "yardage_max"
                ),
                "notes": pattern.get(
                    "notes"
                ),
                "price": pattern.get(
                    "price"
                ),
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

    return pd.DataFrame(
        detail_rows
    )


def data_collection_pipeline(category, total):
    """
    Search Ravelry, collect pattern details,
    and save them to the refresh directory.

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

    print()
    print(
        f"Searching for {total} "
        f"{category} patterns..."
    )

    patterns = unique_pattern_collection(
        category,
        total,
    )

    if len(patterns) != total:
        raise ValueError(
            f"Requested {total} {category} patterns "
            f"but search returned only {len(patterns)}."
        )

    print(
        "Collecting pattern details..."
    )

    details = detail_collector(
        patterns
    )

    if len(details) != total:
        raise ValueError(
            f"Expected {total} detailed {category} patterns "
            f"but collected {len(details)}."
        )

    # Create data/refresh/ if it does not exist.
    REFRESH_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        REFRESH_DIR
        / f"{category}_details.csv"
    )

    details.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Saved {len(details)} patterns to:"
    )

    print(
        output_path
    )

    return details


def collect_all_pattern_data():
    """
    Collect every pattern category configured
    in PATTERN_CATEGORIES.
    """

    for category, total in PATTERN_CATEGORIES.items():

        print()
        print(
            "=" * 60
        )

        print(
            f"Starting collection for "
            f"{category}..."
        )

        print(
            "=" * 60
        )

        data_collection_pipeline(
            category=category,
            total=total,
        )

    print()
    print(
        "All pattern categories collected successfully."
    )

    print(
        f"Refresh data saved in: {REFRESH_DIR}"
    )


if __name__ == "__main__":
    collect_all_pattern_data()