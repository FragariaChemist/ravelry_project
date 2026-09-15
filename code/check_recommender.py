from pathlib import Path
import time

import joblib
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_distances

from recommender import (
    NUMERICAL_FEATURES,
    prepare_numeric_features,
    build_neighbor_model,
    find_neighbors,
)


# Settings
TARGET_PATTERN = "Classic Ribbed Hat"
N_NEIGHBORS = 5


# File locations
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = (
    PROJECT_DIR
    / "data"
    / "rav_clean.csv"
)

ARTIFACT_DIR = (
    PROJECT_DIR
    / "artifacts"
)


# Load data
patterns = pd.read_csv(DATA_PATH)

start = time.time()


# Load previously built recommender artifacts
feature_matrix = load_npz(
    ARTIFACT_DIR / "feature_matrix.npz"
)

encoder = joblib.load(
    ARTIFACT_DIR / "encoder.joblib"
)

scaler = joblib.load(
    ARTIFACT_DIR / "scaler.joblib"
)


# Build nearest-neighbor model
model = build_neighbor_model(feature_matrix)


# Find the target pattern
matching_indices = patterns.index[
    patterns["name"] == TARGET_PATTERN
]

if len(matching_indices) == 0:
    raise ValueError(
        f"Pattern '{TARGET_PATTERN}' was not found."
    )

target_index = matching_indices[0]


# Find nearest neighbors
distances, indices = find_neighbors(
    model,
    feature_matrix,
    target_index,
    N_NEIGHBORS,
)


# Create recommendation results
results = patterns.iloc[indices][
    [
        "name",
        "author",
        "yarn_weight",
        "type",
    ]
].copy()

results["distance"] = distances


# Find where each feature group begins and ends
categorical_count = len(
    encoder.get_feature_names_out()
)

numeric_count = len(
    scaler.mean_
)

categorical_end = categorical_count
numeric_end = categorical_end + numeric_count


# Compare target pattern with each recommendation
# using each feature group separately
print("\nDistance by feature group:")

for neighbor_index in indices:
    name = patterns.iloc[neighbor_index]["name"]

    categorical_distance = cosine_distances(
        feature_matrix[
            target_index,
            :categorical_end,
        ],
        feature_matrix[
            neighbor_index,
            :categorical_end,
        ],
    )[0, 0]

    numeric_distance = cosine_distances(
        feature_matrix[
            target_index,
            categorical_end:numeric_end,
        ],
        feature_matrix[
            neighbor_index,
            categorical_end:numeric_end,
        ],
    )[0, 0]

    text_distance = cosine_distances(
        feature_matrix[
            target_index,
            numeric_end:,
        ],
        feature_matrix[
            neighbor_index,
            numeric_end:,
        ],
    )[0, 0]

    print(
        name,
        "| categorical:",
        round(categorical_distance, 3),
        "| numeric:",
        round(numeric_distance, 3),
        "| text:",
        round(text_distance, 3),
    )


# Print target pattern
print("\nOriginal pattern:")

print(
    patterns.loc[
        target_index,
        [
            "name",
            "author",
            "yarn_weight",
            "type",
        ],
    ]
)


# Print recommendations
print("\nRecommendations:")

print(results)


# Print feature matrix information
print(
    "\nFeature matrix shape:",
    feature_matrix.shape,
)

print(
    "Seconds:",
    round(time.time() - start, 1),
)


# Compare original numeric values
comparison_indices = [
    target_index,
    *indices,
]

print("\nOriginal numeric values:")

print(
    patterns.iloc[comparison_indices][
        [
            "name",
            *NUMERICAL_FEATURES,
        ]
    ]
)


# Apply the same numeric preparation used by the recommender
numeric_features = prepare_numeric_features(
    patterns
)

scaled_numeric = scaler.transform(
    numeric_features
)

scaled_numeric_df = pd.DataFrame(
    scaled_numeric,
    columns=NUMERICAL_FEATURES,
    index=patterns.index,
)

scaled_numeric_df.insert(
    0,
    "name",
    patterns["name"],
)


print("\nScaled numeric values:")

print(
    scaled_numeric_df.iloc[
        comparison_indices
    ]
)


# Inspect the raw popularity distributions
print("\nPopularity feature distribution:")

print(
    patterns[
        [
            "projects_count",
            "queued_projects_count",
        ]
    ].describe(
        percentiles=[
            0.50,
            0.75,
            0.90,
            0.95,
            0.99,
        ]
    ).round(2)
)