from pathlib import Path
import time

import joblib
import pandas as pd
import spacy
from scipy.sparse import save_npz

from recommender import build_feature_matrix


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


def build_recommender():
    """Build and save recommender artifacts."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned pattern data was not found: "
            f"{DATA_PATH}"
        )

    print("Loading pattern data...")
    patterns = pd.read_csv(DATA_PATH)

    print(f"Loaded {len(patterns)} patterns.")

    print("Loading spaCy model...")
    nlp = spacy.load("en_core_web_md")

    print("Building feature matrix...")
    start = time.time()

    (
        feature_matrix,
        encoder,
        scaler,
        vectorizer,
    ) = build_feature_matrix(
        patterns,
        nlp,
    )

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Saving artifacts...")

    save_npz(
        ARTIFACT_DIR / "feature_matrix.npz",
        feature_matrix,
    )

    joblib.dump(
        encoder,
        ARTIFACT_DIR / "encoder.joblib",
    )

    joblib.dump(
        scaler,
        ARTIFACT_DIR / "scaler.joblib",
    )

    joblib.dump(
        vectorizer,
        ARTIFACT_DIR / "vectorizer.joblib",
    )

    elapsed = time.time() - start

    print()
    print("Done.")
    print("Feature matrix shape:", feature_matrix.shape)
    print("Seconds:", round(elapsed, 1))
    print("Artifacts saved to:", ARTIFACT_DIR)


if __name__ == "__main__":
    build_recommender()
    