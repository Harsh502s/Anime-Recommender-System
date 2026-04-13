import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
import spacy
import pickle

nlp = spacy.load("en_core_web_sm")
from ast import literal_eval as le
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import warnings as w

w.filterwarnings("ignore")


stopwords_nltk = stopwords.words("english")
stopwords_spacy = spacy.lang.en.stop_words.STOP_WORDS
stopwords = set(stopwords_nltk + list(stopwords_spacy))
pd.set_option("display.max_columns", None)
df = pd.read_csv("anime_data.csv")
df.reset_index(inplace=True)
url_df = pd.read_csv("anime_url.csv")
url_df.reset_index(inplace=True)
pd.set_option("display.max_columns", None)
df = url_df.merge(df, on='index',how='left')
df.drop(['index'],axis=1,inplace=True)
df.anime_producer = df.anime_producer.replace("['NA']", df.anime_producer.mode()[0])
df.anime_studio = df.anime_studio.replace(np.nan, df.anime_studio.mode()[0])
df.anime_mal_score = pd.to_numeric(df.anime_mal_score, errors="coerce")
df.anime_mal_score = df.anime_mal_score.replace(np.nan, df.anime_mal_score.median())
df.dropna(inplace=True)
df.drop_duplicates(inplace=True,keep='first')
df.anime_genres = df.anime_genres.apply(le)
df.anime_producer = df.anime_producer.apply(le)
df.anime_genres = df.anime_genres.apply(lambda x: [i.replace(" ", "") for i in x])
df.anime_studio = df.anime_studio.apply(lambda x: x.replace(" ", ""))
df.anime_studio = df.anime_studio.apply(lambda x: x.split())
# Text Preprocessing
df['anime_overview'] =  df['anime_overview'].apply(lambda x: x.split(r"[Written by MAL Rewrite]")[0])

# Taking Only Words
df['anime_overview'] = df['anime_overview'].apply(lambda x: " ".join(re.findall(r'[a-zA-Z]+', x)).lower())

# Removing all s and t from the overview which are not in the form of words

df['anime_overview'] = df['anime_overview'].apply(lambda x: re.sub(r'\bs\b|\bt\b','',x))

# Dropping the index column and resetting the index to new values
df.reset_index(drop=True, inplace=True)
df.reset_index(inplace=True)
# Changing the column names
df.rename(
    columns={
        "index": "anime_id",
        "anime_urls": "urls",
        "anime_overview": "overview",
        "anime_genres": "genres",
        "anime_producer": "producer",
        "anime_studio": "studio",
        "anime_mal_score": "score",
        "anime_poster": "poster",
        "anime_title": "title",
    },
    inplace=True,
)
# Making tags as a combination of overview, genres and studio
df.overview = df.overview.astype(str)
df.overview = df.overview.apply(lambda x: x.split())

df['tags'] = df['overview'] + df['genres'] + df['studio']
df['tags'] = df['tags'].apply(lambda x:[i.lower() for i in x])
df['tags'] = df['tags'].apply(lambda x: ' '.join(x))
# Lemmatizing the tags

def stemmer(text):
    doc = nlp(text)
    doc = [token.lemma_ for token in doc if token.lemma_ not in stopwords]
    return ' '.join(doc)

df['tags'] = df['tags'].apply(stemmer)
# CountVectorizer to convert tags into matrix

vectorizer = TfidfVectorizer(analyzer='word',max_features=10000,ngram_range=(1,3),norm='l2')
vector = vectorizer.fit_transform(df['tags']).toarray()
print(vector.shape)
# Cosine similarity

similarity = cosine_similarity(vector)
similarity[0]
def recommend(anime):
    index = df[df['title'] == anime].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:11]
    for i in distances:
        print(df.iloc[i[0]].title)
        pass
    
recommend('Naruto')
df.to_csv("rec_data.csv", index=False)
df.to_csv(r"D:\Github\Anime-Recommender\rec_data.csv", index=False)
pickle.dump(similarity, open(r"D:\Github\Anime-Recommender\similarity.pkl", "wb"))
pickle.dump(similarity, open(r"similarity.pkl", "wb"))