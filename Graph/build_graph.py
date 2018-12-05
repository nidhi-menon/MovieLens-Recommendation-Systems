import pandas as pd
import numpy as np
from py2neo import Graph, authenticate
import time

# Connecting to Neo4j instance
authenticate("localhost:7474",'neo4j','test123')
graph = Graph('http://localhost:7474/db/data/')

# Reading user data
user = pd.read_csv('ml-100k/u.user', sep='|', header=None, names=['id','age','gender','occupation','zip code'], encoding='latin-1')

# Reading genre data
genre = pd.read_csv('ml-100k/u.genre', sep='|', header=None, names=['name', 'id'], encoding='latin-1')

# Reading movie data
movie_col = ['id', 'title','release date', 'useless', 'IMDb url']
movie_col = movie_col + genre['id'].tolist()
movie = pd.read_csv('ml-100k/u.item', sep='|', header=None, names=movie_col, encoding='latin-1')
movie = movie.fillna('unknown')

# Reading rating data
rating_col = ['user_id', 'item_id','rating', 'timestamp']
rating = pd.read_csv('ml-100k/u.data', sep='\t' ,header=None, names=rating_col, encoding='latin-1')



# Creating nodes for every user, identified by User ID
tx = graph.begin()
statement = "MERGE (a:`User`{user_id:{A}}) RETURN a"
for u in user['id']:
    tx.run(statement, {"A": u})
tx.commit()


# Creating nodes for every genre
tx = graph.begin()
statement = "MERGE (a:`Genre`{genre_id:{A}, name:{B}}) RETURN a"
for g,row in genre.iterrows() :
    tx.run(statement, {"A": row.iloc[1], "B": row.iloc[0]})
tx.commit()


# Creating nodes for every movie and adding the Is_genre relationship between movies and genre nodes
tx = graph.begin()
statement1 = "MERGE (a:`Movie`{movie_id:{A}, title:{B}, url:{C}}) RETURN a"
statement2 = ("MATCH (t:`Genre`{genre_id:{D}}) "
              "MATCH (a:`Movie`{movie_id:{A}, title:{B}, url:{C}}) MERGE (a)-[r:`Is_genre`]->(t) RETURN r")
for m,row in movie.iterrows() :
    tx.run(statement1, {"A": row.loc['id'], "B": row.loc['title'], "C": row.loc['IMDb url']})
    is_genre = row.iloc[-19:]==1
    related_genres = genre[is_genre].axes[0].values
    for g in related_genres :
        x = int(g)
        tx.run(statement2, {"A": row.loc['id'], "B": row.loc['title'], "C": row.loc['IMDb url'], "D": x})
tx.commit()


# Creating the Has_rated edge between user and movie nodes
tx = graph.begin()
statement = ("MATCH (u:`User`{user_id:{A}}) "
             "MATCH (m:`Movie`{movie_id:{C}}) MERGE (u)-[r:`Has_rated`{rating:{B}}]->(m) RETURN r")
count = 0
for r,row in rating.iterrows() :
    tx.run(statement, {"A": int(row.loc['user_id']), "B": int(row.loc['rating']), "C": int(row.loc['item_id'])})
    count += 1
    # Committing 100 queries at a time to prevent one massive commit at the end
    if count%100 == 0:
        tx.process()
tx.commit()


# Creating indexes to speed up queries
graph.run('CREATE INDEX ON :User(user_id)')
graph.run('CREATE INDEX ON :Movie(movie_id)')
graph.run('CREATE INDEX ON :Genre(genre_id)')
