import pandas as pd
import spacy

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import hstack
import numpy as np


CATEGORICAL_FEATURES = [
    'author',
    'yarn_weight',
    'type',
]


NUMERICAL_FEATURES = [
    'difficulty_avg',
    'gauge_per_inch',
    'max_yardage',
    'price',
    'projects_count',
    'queued_projects_count',
    'rating_avg',
]


LOG_FEATURES = [
    "projects_count",
    "queued_projects_count",
]

def preprocess_notes(notes,nlp):
    '''Lemmetize pattern notes and remove stop words and non-word tokens'''
    processed_notes = []

    for doc in nlp.pipe(
        notes, 
        batch_size=100,
        disable=["parser", "ner"]
    ):
        tokens = [
            token.lemma_.lower().strip()
            for token in doc
            if token.is_alpha
            and not token.is_stop
            and len(token.text) > 1
        ]
        processed_notes.append(" ".join(tokens))

    return processed_notes


def prepare_pattern_text(patterns, nlp):
    '''Create cleaned text features from the pattern notes'''

    patterns  = patterns.copy()

    patterns['processed_text'] = preprocess_notes(
        patterns['notes'],
        nlp,
    )

    empty_text = patterns['processed_text'].eq('')

    patterns.loc[empty_text, 'processed_text'] = patterns.loc[
        empty_text,
        'type',
    ]

    return patterns


def build_categorical_features(patterns):
    '''One-hot encode categorical features'''

    encoder = OneHotEncoder(
        handle_unknown= 'ignore',
        sparse_output=True,
    )

    categorical_matrix = encoder.fit_transform(
        patterns[CATEGORICAL_FEATURES]
    )

    return categorical_matrix, encoder


def prepare_numeric_features(patterns):
    """Prepare numeric features before scaling."""

    numeric_features = patterns[NUMERICAL_FEATURES].copy()

    for feature in LOG_FEATURES:
        numeric_features[feature] = np.log1p(
            numeric_features[feature]
        )

    return numeric_features

def build_numeric_features(patterns):
    """Standardize numeric pattern features."""

    numeric_features = prepare_numeric_features(patterns)

    scaler = StandardScaler()

    numeric_matrix = scaler.fit_transform(
        numeric_features
    )

    return numeric_matrix, scaler

def build_text_features(patterns):
        '''Convert processed pattern notes into TF-IDF features'''

        vectorizer = TfidfVectorizer(
             max_features=3000,
        )

        test_matrix = vectorizer.fit_transform(
             patterns['processed_text']
        )

        return test_matrix, vectorizer


def build_feature_matrix(patterns, nlp):
     '''Combine categorical, numeric, and text features'''

     patterns = prepare_pattern_text(patterns, nlp)

     categorical_matrix, encoder = build_categorical_features(patterns)
     numeric_matrix, scaler = build_numeric_features(patterns)
     text_matrix, vectorizer = build_text_features(patterns)

     feature_matrix = hstack([
         categorical_matrix,
         numeric_matrix,
         text_matrix,
     ]).tocsr()

     return feature_matrix, encoder, scaler, vectorizer


def build_neighbor_model(feature_matrix):
     '''Fit a nearest-neighbor model using cosine distance'''

     model = NearestNeighbors(
          metric='cosine',
          algorithm = 'brute',
     )

     model.fit(feature_matrix)

     return model

def find_neighbors(model, feature_matrix, pattern_index, n_neighbors=5):
     '''Return the nearest pattern incides and their cosine distances'''

     distances, indices = model.kneighbors(
          feature_matrix[pattern_index],
          n_neighbors=n_neighbors +1,
     )

     return distances[0][1:], indices[0][1:]