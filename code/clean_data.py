from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
REFRESH_DIR = DATA_DIR / "refresh"


# Read the newly refreshed raw data.
HAT_PATH = REFRESH_DIR / "beanie-toque_details.csv"
SOCK_PATH = REFRESH_DIR / "mid-calf_details.csv"
PULLOVER_PATH = REFRESH_DIR / "pullover_details.csv"


# Save the cleaned refreshed dataset separately
# from the original known-good rav_clean.csv.
OUTPUT_PATH = REFRESH_DIR / "rav_clean.csv"


# --------------------------------------------------
# Yarn-weight cleaning rules
# --------------------------------------------------

YARN_WEIGHT_REPLACEMENTS = {
    "Aran / Worsted": "Worsted",
    "DK / Sport": "DK",
}


# Typical gauge per four inches for each yarn weight.
# These values come from the original project.
YARN_WEIGHT_GAUGE = {
    "Worsted": 20,
    "DK": 22,
    "Bulky": 16,
    "Aran": 20,
    "Super Bulky": 12,
    "Fingering": 32,
    "Sport": 24,
    "Any gauge": 20,
    "Unavailable": 20,
    "Light Fingering": 32,
    "Jumbo": 5,
    "Lace": 40,
}


# --------------------------------------------------
# Yardage cleaning rules
# --------------------------------------------------

# Minimum number of known yardage values required
# before we trust the current dataset's group mean.
MIN_YARDAGE_GROUP_COUNT = 10


# Fallback yardage values from the original project.
# These are used only when the current dataset has
# too few examples for a reliable yarn-weight/type mean.
YARN_WEIGHT_YARDAGE = {
    "Worsted": {
        "hat": 213.0,
        "pullover": 1781.0,
        "socks": 326.0,
    },
    "DK": {
        "hat": 253.0,
        "pullover": 1840.0,
        "socks": 386.0,
    },
    "Bulky": {
        "hat": 142.0,
        "pullover": 1408.0,
        "socks": 329.0,
    },
    "Aran": {
        "hat": 188.0,
        "pullover": 1552.0,
        "socks": 399.0,
    },
    "Super Bulky": {
        "hat": 99.0,
        "pullover": 1077.0,
        "socks": 187.0,
    },
    "Fingering": {
        "hat": 301.0,
        "pullover": 2137.0,
        "socks": 429.0,
    },
    "Sport": {
        "hat": 274.0,
        "pullover": 2129.0,
        "socks": 430.0,
    },
    "Any gauge": {
        "hat": 259.0,
        "pullover": 2869.0,
        "socks": 450.0,
    },
    "Unavailable": {
        "hat": 225.0,
        "pullover": 2309.0,
        "socks": 331.0,
    },
    "Light Fingering": {
        "hat": 345.0,
        "pullover": 2118.0,
        "socks": 452.0,
    },
    "Jumbo": {
        "hat": 124.0,
        "pullover": 1752.0,
        "socks": 264.0,
    },
    "Lace": {
        "hat": 250.0,
        "pullover": 1844.0,
        "socks": 610.0,
    },
}


def load_pattern_data():
    """Load the three raw garment datasets."""

    hats = pd.read_csv(
        HAT_PATH
    )

    socks = pd.read_csv(
        SOCK_PATH
    )

    pullovers = pd.read_csv(
        PULLOVER_PATH
    )

    return hats, socks, pullovers


def add_pattern_types(hats, socks, pullovers):
    """Add the garment type to each dataset."""

    hats = hats.copy()
    socks = socks.copy()
    pullovers = pullovers.copy()

    hats["type"] = "hat"
    socks["type"] = "socks"
    pullovers["type"] = "pullover"

    return hats, socks, pullovers


def clean_yarn_weights(hats, socks, pullovers):
    """Standardize unusual yarn-weight labels."""

    hats = hats.copy()
    socks = socks.copy()
    pullovers = pullovers.copy()

    hats["yarn_weight"] = hats[
        "yarn_weight"
    ].replace(
        YARN_WEIGHT_REPLACEMENTS
    )

    socks["yarn_weight"] = socks[
        "yarn_weight"
    ].replace(
        YARN_WEIGHT_REPLACEMENTS
    )

    pullovers["yarn_weight"] = pullovers[
        "yarn_weight"
    ].replace(
        YARN_WEIGHT_REPLACEMENTS
    )

    # Remove yarn weights that occur too rarely
    # to be useful to the recommender.
    pullovers = pullovers[
        ~pullovers["yarn_weight"].isin(
            [
                "Thread",
                "Cobweb",
            ]
        )
    ].copy()

    return hats, socks, pullovers


def combine_pattern_data(hats, socks, pullovers):
    """Combine all garment datasets into one DataFrame."""

    patterns = pd.concat(
        [
            hats,
            socks,
            pullovers,
        ],
        ignore_index=True,
    )

    return patterns


def drop_unused_columns(patterns):
    """Remove columns not used by the recommender."""

    patterns = patterns.copy()

    patterns = patterns.drop(
        columns=[
            "sizes_available",
            "gauge_pattern",
        ]
    )

    return patterns


def gauge_calculator(row):
    """
    Fill a missing gauge using the pattern's
    yarn weight.
    """

    if pd.isna(row["gauge"]):

        return YARN_WEIGHT_GAUGE.get(
            row["yarn_weight"]
        )

    return row["gauge"]


def build_yardage_stats(patterns):
    """
    Calculate current yardage averages and counts
    for each yarn-weight and garment-type combination.
    """

    yardage_stats = patterns.groupby(
        [
            "yarn_weight",
            "type",
        ]
    )["max_yardage"].agg(
        [
            "count",
            "mean",
        ]
    )

    return yardage_stats


def yardage_calculator(row, yardage_stats):
    """
    Fill missing maximum yardage using the current
    dataset when enough examples are available.

    Fall back to the original project averages for
    groups with too few observations.
    """

    # If the pattern already has a yardage,
    # keep the original value.
    if not pd.isna(
        row["max_yardage"]
    ):
        return row["max_yardage"]

    yarn_weight = row[
        "yarn_weight"
    ]

    pattern_type = row[
        "type"
    ]

    group = (
        yarn_weight,
        pattern_type,
    )

    # Use the current dataset mean if the group
    # contains enough known yardage values.
    if group in yardage_stats.index:

        stats = yardage_stats.loc[
            group
        ]

        if (
            stats["count"]
            >= MIN_YARDAGE_GROUP_COUNT
        ):
            return stats["mean"]

    # Otherwise use the original project's
    # fallback value.
    return YARN_WEIGHT_YARDAGE.get(
        yarn_weight,
        {},
    ).get(
        pattern_type
    )


def fill_missing_values(patterns):
    """Fill null values using the project cleaning rules."""

    patterns = patterns.copy()

    # Build yardage statistics from the current dataset.
    yardage_stats = build_yardage_stats(
        patterns
    )

    patterns["max_yardage"] = patterns.apply(
        lambda row: yardage_calculator(
            row,
            yardage_stats,
        ),
        axis=1,
    )

    patterns["gauge"] = patterns.apply(
        gauge_calculator,
        axis=1,
    )

    patterns = patterns.fillna(
        {
            "gauge_divisor": 4.0,
            "notes": "notes not provided",
            "price": 0,
        }
    )

    return patterns


def add_gauge_per_inch(patterns):
    """Normalize gauge to stitches per inch."""

    patterns = patterns.copy()

    patterns["gauge_per_inch"] = (
        patterns["gauge"]
        / patterns["gauge_divisor"]
    )

    return patterns


def clean_pattern_data():
    """Run the complete pattern-cleaning pipeline."""

    print(
        "Loading garment datasets..."
    )

    hats, socks, pullovers = load_pattern_data()

    print(
        "Raw rows:",
        len(hats)
        + len(socks)
        + len(pullovers),
    )

    hats, socks, pullovers = add_pattern_types(
        hats,
        socks,
        pullovers,
    )

    hats, socks, pullovers = clean_yarn_weights(
        hats,
        socks,
        pullovers,
    )

    patterns = combine_pattern_data(
        hats,
        socks,
        pullovers,
    )

    patterns = drop_unused_columns(
        patterns
    )

    patterns = fill_missing_values(
        patterns
    )

    patterns = add_gauge_per_inch(
        patterns
    )

    # Verify that cleaning did not leave
    # unexpected missing values behind.
    remaining_nulls = patterns.isna().sum()

    remaining_nulls = remaining_nulls[
        remaining_nulls > 0
    ]

    if not remaining_nulls.empty:

        print(
            "\nWarning: null values remain:"
        )

        print(
            remaining_nulls
        )

        raise ValueError(
            "Cleaning finished with "
            "null values remaining."
        )

    patterns.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"Clean rows: {len(patterns)}"
    )

    print(
        f"Saved cleaned data to: "
        f"{OUTPUT_PATH}"
    )

    return patterns


if __name__ == "__main__":
    clean_pattern_data()