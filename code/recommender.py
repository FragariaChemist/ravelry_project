import pandas as pd
import spacy

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler


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