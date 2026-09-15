from pathlib import Path

import pandas as pd
import streamlit as st
from fuzzywuzzy import process
from scipy.sparse import load_npz

from recommender import (
    build_neighbor_model,
    find_neighbors,
)


# File locations
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "data" / "rav_clean.csv"
ARTIFACT_DIR = PROJECT_DIR / "artifacts"


# Ravelry URL prefix
RAVELRY_URL = "https://www.ravelry.com/patterns/library/"


# Page setup
st.set_page_config(
    page_title="Ravelry Knitting Pattern Recommender",
    page_icon="🧶",
    layout="centered",
)

st.title("Ravelry Pattern Recommender 🧶")


@st.cache_data
def load_patterns():
    """Load the cleaned Ravelry pattern data."""

    return pd.read_csv(DATA_PATH)


@st.cache_resource
def load_recommender():
    """Load the feature matrix and create the nearest-neighbor model."""

    feature_matrix = load_npz(
        ARTIFACT_DIR / "feature_matrix.npz"
    )

    model = build_neighbor_model(
        feature_matrix
    )

    return feature_matrix, model


# Load pattern data and recommender
patterns = load_patterns()

feature_matrix, model = load_recommender()


# User input
pattern_input = st.text_input(
    "Enter a knitting pattern you like. "
    "We'll make a best guess based on your input."
).strip()


if st.button("Submit"):

    if not pattern_input:
        st.write("Please enter a pattern name.")

    else:
        # Find the closest pattern name to the user's input
        pattern_names = patterns["name"].tolist()

        fuzzy_match = process.extractOne(
            pattern_input,
            pattern_names,
        )

        matched_name = fuzzy_match[0]


        # Find the corresponding pattern row
        matching_rows = patterns[
            patterns["name"] == matched_name
        ]

        if matching_rows.empty:
            st.write(
                "No patterns like this were found "
                "in the database."
            )

        else:
            pattern_index = matching_rows.index[0]

            matched_pattern = patterns.loc[
                pattern_index
            ]

            matched_url = (
                RAVELRY_URL
                + matched_pattern["permalink"]
            )


            # Show the pattern we matched
            st.write(
                f"We think you are looking for "
                f"**{matched_name}**:"
            )

            st.write(matched_url)


            # Find the five nearest patterns
            _, neighbor_indices = find_neighbors(
                model,
                feature_matrix,
                pattern_index,
                5,
            )


            st.subheader("You might also like:")


            # Display recommendations
            for neighbor_index in neighbor_indices:
                recommendation = patterns.iloc[
                    neighbor_index
                ]

                recommendation_url = (
                    RAVELRY_URL
                    + recommendation["permalink"]
                )

                st.write(
                    f"**{recommendation['name']}**"
                )

                st.write(
                    recommendation_url
                )


# About the project
st.write("")
st.write("")

st.write(
    "This application consists of just shy of 15,000 "
    "popular hat, pullover, and sock patterns found on "
    "Ravelry and is meant to be a proof of concept. "
    "Please visit Ravelry to explore their full library "
    "of patterns."
)

st.write("")

st.write("Application by Kristina Halbig")