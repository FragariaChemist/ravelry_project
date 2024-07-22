import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process
import boto3
from io import StringIO

# Website page setup
st.set_page_config(
    page_title="Ravelry Knitting Pattern Recommender",
    page_icon="🧶",
    layout="centered",
)

st.title('Ravelry Pattern Recommender 🧶')
st.write("")
st.write("")
st.write("")
st.write("")

# AWS Credentials
aws_credentials = st.secrets['aws']

# S3 Client
s3 = boto3.client(
    's3',
    aws_access_key_id = aws_credentials['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key = aws_credentials['AWS_SECRET_ACCESS_KEY']
)

# Reading in data from AWS S3 bucket
@st.cache_data # Read in the data once and only once - from streamlit documentation
def load_df(bucket, key):
    obj = s3.get_object(Bucket = bucket, Key = key)
    df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')), index_col = 'pattern_name')
    return df

@st.cache_data
def load_permalink(bucket, key):
    obj = s3.get_object(Bucket = bucket, Key = key)
    df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
    return df

# Load the required data to run recommender
bucket_name = 'ravelry'
rav_rec_df = load_df(bucket_name, 'rav_rec.csv')
permalink_df = load_permalink(bucket_name, 'permalink.csv')

txt = st.text_area(r"$\textsf{\large Enter a knitting pattern you like! We'll make a best guess based on your input.}$").strip()

# Actual recommender function
if st.button('Submit'):
    choices = rav_rec_df.columns
    fuzzy_process = process.extractOne(txt, choices)
    fuzzy_choice = fuzzy_process[0]
    matching_row = permalink_df[permalink_df['pattern_name'] == fuzzy_choice]
    # For when FuzzyWuzzy just can't find anything in the permalink_df that matches what the user type
    # For example 'power flower mittens'
    if not matching_row.empty:
        patt_link = matching_row['permalink'].iloc[0]
        url_prefix = 'https://www.ravelry.com/patterns/library/'
        st.write(f'We think you are looking for the pattern titled {fuzzy_choice}: {url_prefix}{patt_link}')

        top_five = list(rav_rec_df[fuzzy_choice].sort_values().iloc[1:6].index)

        for patt in top_five:
            top_matching_row = permalink_df[permalink_df['pattern_name'] == patt]
            top_patt_link = top_matching_row['permalink'].iloc[0]
            url = f'{patt}: {url_prefix}{top_patt_link}'  
            st.write(url)

    else:
        st.write('No patterns found like this in our database.')

# Notes about recommender
st.write("")
st.write("")
st.write("")
st.write('This application consists just shy of 15,000 popular hat, pullover, and sock patterns found on Ravelry and only meant to be a proof of concept.  Please visit Ravelry to explore their full (over one million!) library of patterns.')
st.write("")
st.write('Application by Kristina Halbig')