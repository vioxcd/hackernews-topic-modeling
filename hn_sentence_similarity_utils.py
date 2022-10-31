# %% [code]
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('omw-1.4')
lemmatizer = WordNetLemmatizer()

def load_data(fp):
    df = pd.read_csv(fp,
                     usecols=['title', 'url', 'id', 'timestamp_formatted'],
                     parse_dates=['timestamp_formatted'])
    return df.rename(columns={"timestamp_formatted": "ts"})

def remove_one_word(title: pd.Series) -> pd.Series:
    f = (
        title
         .str
         .split()
         .apply(lambda x: len(x) if type(x) == list else 1)  # avoid weird float error :/
         .apply(lambda x: False if x == 1 else True)
    )
    return title.loc[f]
    
def remove_job_postings(title: pd.Series) -> pd.Series:
    f = (
        title
         .str
         .count('–')
         .apply(lambda x: False if x > 1 else True)  # risk losing some title, but yeh
    )
    return title.loc[f]

def remove_links(title: pd.Series) -> pd.Series:
    f = (
        title
         .str
         .lower()
         .str
         .contains('https?:\s*')
         .values
    )
    # invert bool filters because "regex aren't really for negative matching"
    return title.loc[~f]

def clean_non_stories(title: pd.Series) -> pd.Series:
    return title.str.split("HN: ").apply(lambda x: x[-1])

def clean_last_word_year_and_pdf(title: pd.Series) -> pd.Series:
    pat = r'\s\(\d+\)|\s\[pdf\]'
    return title.str.replace(pat, '', regex=True)

def lemmatize(title: pd.Series, lemmatizer=lemmatizer) -> pd.Series:
    return (
        title.str.split(" ")
             .apply(lambda row_list: [lemmatizer.lemmatize(word) for word in row_list])
             .apply(lambda x: " ".join(x))
    )

def finalizes(title: pd.Series) -> pd.Series:
    """finalizes the cleaning process by getting the copy of the passed-around view"""
    return title.copy().reset_index(drop=True)