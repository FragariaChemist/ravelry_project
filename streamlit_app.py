import pandas as pd
import streamlit as st
import boto3
from io import BytesIO
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 

# Load secrets for Streamlit Cloud
AWS_ACCESS_KEY_ID = st.secrets["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = st.secrets["AWS_SECRET_ACCESS_KEY"]
S3_BUCKET_NAME = st.secrets["S3_BUCKET_NAME"]

# S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

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

@st.cache_data # Read in the data once and only once - from streamlit documentation
def load_df_from_aws(file):
    obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=file)
    data = obj['Body'].read()
    chunksize = 25000  # Adjust this value as needed
    chunks = []
    for chunk in pd.read_csv(BytesIO(data), chunksize=chunksize):
        chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    return df

@st.cache_data
def load_permalink_from_aws(file):
    obj = s3.get_object(Bucket = S3_BUCKET_NAME, Key = file)
    data = obj['Body'].read()
    return pd.read_csv(BytesIO(data))
    
rav_rec_df = load_df_from_aws('rav_rec.csv')
permalink_df = load_permalink_from_aws('permalink.csv')

txt = st.text_area(r"$\textsf{\large Enter a knitting pattern you like! We'll make a best guess based on your input.}$").strip()


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

st.write("")
st.write("")
st.write("")
st.write('This application consists just shy of 15,000 popular hat, pullover, and sock patterns found on Ravelry and only meant to be a proof of concept.  Please visit Ravelry to explore their full (over one million!) library of patterns.')
st.write("")
st.write('Application by Kristina Halbig')