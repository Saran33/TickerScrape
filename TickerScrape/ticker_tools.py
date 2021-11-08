import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz

def extract_bond_country(name):
    countries_df = pd.read_csv('csv_files/country_dataset.csv')
    name_str = name.strip().split()
    if name_str[0] == 'U.K.':
        country_name = 'United Kingdom'
    elif name_str[0] == 'U.S.':
        country_name = 'United States of America'
    elif name_str[0] == 'United States':
        country_name = 'United States of America'
    else:
        test_str = name_str[0] +' '+ name_str[1]
        print(test_str)
        highest = process.extractOne(test_str,countries_df['Country'], scorer=fuzz.token_set_ratio)
        print(highest[0])
        country_name = countries_df.loc[countries_df['Country'].str.contains(highest[0])]['Country'].values[0]
    return country_name