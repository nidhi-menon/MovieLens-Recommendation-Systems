from imdb import IMDb
from py2neo import Graph, authenticate
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, Response, json
from lxml import html
import requests
import collections
import itertools
from gensim import corpora, models, similarities
import gensim
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk
from nltk.stem import SnowballStemmer


ia = IMDb()
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

# Reading User data from file
user = pd.read_csv('ml-100k/u.user', sep='|', header=None, names=['id','age','gender','occupation','zip code'], encoding='latin-1')

# Reading Genre data from file
genre = pd.read_csv('ml-100k/u.genre', sep='|', header=None, names=['name', 'id'], encoding='latin-1')


# Reading Movie data from file
movie_col = ['id', 'title','release date', 'useless', 'IMDb url']
movie_col = movie_col + genre['id'].tolist()
movie = pd.read_csv('ml-100k/u.item', sep='|', header=None, names=movie_col, encoding='latin-1')
movie = movie.fillna('unknown')

# Reading Rating data from file
rating_col = ['user_id', 'item_id','rating', 'timestamp']
rating = pd.read_csv('ml-100k/u.data', sep='\t' ,header=None, names=rating_col, encoding='latin-1')
n_r = rating.shape[0]

# Initializing new fields in movie dataframe
movie['synopsis'] = ''
movie['storyline'] = ''
movie['description']= ''
movie['text'] = ''

# Extracting movie synopsis from IMDB resource
for index, row in movie.iterrows():
    if row.text.strip() == '':
        title = row.title
        title = title.replace('(', '')
        title = title.replace(')', '')
        title = title.replace(',', '')
        ia = IMDb('http')
        m = ia.search_movie(row.title)
        if len(m) !=0:
            m = m[0]
            try:
                title_found = m['title']+ ' ' +str(m['year'])
                if compare(title.split(), title_found.split()):
                    m = ia.get_movie(m.movieID)
                    movie.loc[index, 'description'] = m.get('plot outline')
                    print("\n\n")
                    print(m.get('plot outline'))
                    ia.update(m, 'synopsis')
                    movie.loc[index, 'synopsis'] = m.get('synopsis')
                    movie.loc[index, 'text'] = movie.loc[index, 'description'] + ' ' + movie.loc[index, 'synopsis']
            except:
                pass

### Preprocessing data for LSA

# Remove punctuations
tokenizer = RegexpTokenizer(r'\w+')
movie['text'] = movie['text'].apply(lambda x: ' '.join(tokenizer.tokenize(x)))
documents = list(movie['text'])

# Get stopwords
stop_words = set(stopwords.words('english'))

# Extract the user name
def extract_entities(name, text):
    for sent in nltk.sent_tokenize(text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            try:
                if chunk.label() == 'PERSON':
                    for c in chunk.leaves():
                        if str(c[0].lower()) not in name:
                            name.append(str(c[0]).lower())
            except AttributeError:
                pass
    return name
names = []
for doc in documents:
    names = extract_entities(names, doc)

# Updating stop_words with names
stop_words.update(names)


# Stemming
stemmer = SnowballStemmer("english")
texts = [[stemmer.stem(word) for word in document.lower().split() if (word not in stop_words)]
          for document in documents]

# Creating dictionary, corpus and then TFIDF transformation
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
numpy_matrix = gensim.matutils.corpus2dense(corpus, num_terms=51556)
s = np.linalg.svd(numpy_matrix, full_matrices=False, compute_uv=False)

# Creating LSA model
lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=30)
index = similarities.MatrixSimilarity(lsi[corpus_tfidf])
movie['similarity'] = 'unknown'
movie['size_similar'] = 0
total_sims = []
thershold = 0.2
for i, doc in enumerate(corpus_tfidf):
    vec_lsi = lsi[doc]
    sims = index[vec_lsi]
    total_sims = np.concatenate([total_sims, sims])
    similarity = []
    for j, x in enumerate(movie.id):
        if sims[j] > thershold:
            similarity.append((x, sims[j]))
    similarity = sorted(similarity, key=lambda item: -item[1])
    movie = movie.set_value(i,'similarity', similarity)
    movie = movie.set_value(i,'size_similar', len(similarity))

# Writing calculated similarity information to file
db_similarity = movie[['id', 'similarity']]
db_similarity.to_csv('u.similarity', sep='|')
