import pandas as pd
import streamlit as st
import pickle

rav_rec_df = pd.read_pickle('../data/rav_rec.pkl')

txt = st.text_area("Enter a knitting pattern you like!  Make sure it's written exactly how the designer formatted the name.").strip()


if st.button('Submit'):
    try:
        top_five = list(rav_rec_df[txt].sort_values().iloc[1:6].index)

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
            "'":''
        }

        # Make a table of the replacements dictionary using .maketrans
        replacement_table = str.maketrans(replacements)

        #Iterate through top five patterns to transform names into their url equivalents
        urls = []
        for patt in top_five:
            url_ready = patt.translate(replacement_table).lower()
            url = f'{patt}: https://www.ravelry.com/patterns/library/{url_ready}'
            urls.append(url)

        for url in urls:
            st.write(url)

    # Return error message if typo or non-existent pattern
    except KeyError:
        st.error('Please check to see if your pattern is typed correctly.  It must be written exactly as designer writes it.')