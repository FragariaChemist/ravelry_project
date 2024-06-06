import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 

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

@st.cache_data # Read in the data once and only once
def load_df(path):
    df = pd.read_csv(path, index_col = 'pattern_name')
    return df

rav_rec_df = load_df('../data/rav_rec.csv')

txt = st.text_area(r"$\textsf{\large Enter a knitting pattern you like! We'll make a best guess based on your input.}$").strip()


if st.button('Submit'):
    choices = rav_rec_df.columns
    fuzzy_process = process.extractOne(txt, choices)
    fuzzy_choice = fuzzy_process[0]
    
    st.markdown(f"""
    <p style='font-size:20px;'>
    We think you are looking for the pattern titled: <strong>{fuzzy_choice}</strong>. 
    Here are five patterns that we think are similar:
    </p>
    """, unsafe_allow_html=True)
    
    try:
        top_five = list(rav_rec_df[fuzzy_choice].sort_values().iloc[1:6].index)

        # Make a dictionary to deal with characters in the pattern name, but not in the url address.
        replacements = {
            '#': '',
            '&': '',
            ' ': '-',
            '/': '-',
            '!': '',
            '@': '-',
            '~': '-',
            ',': '',
            "'":'',
            '"':''
        }

        # Make a table of the replacements dictionary using .maketrans
        replacement_table = str.maketrans(replacements)
    
        #Iterate through top five patterns to transform names into their url equivalents
        for patt in top_five:
            url_ready = patt.translate(replacement_table).lower()
            url = f'{patt}: https://www.ravelry.com/patterns/library/{url_ready}'
            st.write(url)

    # Return error message if typo or non-existent pattern
    except KeyError:
        st.error('Please check to see if your pattern is typed correctly.  It must be written exactly as designer writes it.')
st.write("")
st.write("")
st.write("")
st.write('This application consists of 6000 popular hat, pullover, and sock patterns found on Ravelry and only meant to be a proof of concept.  Please visit Ravelry to explore their full (over one million!) library of patterns.')
st.write("")
st.write('Application by Kristina Halbig')