import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 

rav_rec_df = pd.read_csv('../data/rav_rec.csv', index_col = 'pattern_name')

txt = st.text_area("Enter a knitting pattern you like!  Make sure it's written exactly how the designer formatted the name.").strip()


if st.button('Submit'):
    choices = rav_rec_df.columns
    fuzzy_process = process.extractOne(txt, choices)
    fuzzy_choice = fuzzy_process[0]
    st.write(f'We think you are looking for the pattern titled: {fuzzy_choice}')
    
    try:
        top_five = list(rav_rec_df[fuzzy_choice].sort_values().iloc[1:6].index)
        print(f'This is Top Five: {top_five}')

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
        for patt in top_five:
            url_ready = patt.translate(replacement_table).lower()
            url = f'{patt}: https://www.ravelry.com/patterns/library/{url_ready}'
            st.write(url)

    # Return error message if typo or non-existent pattern
    except KeyError:
        st.error('Please check to see if your pattern is typed correctly.  It must be written exactly as designer writes it.')