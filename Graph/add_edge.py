from py2neo import Graph, authenticate
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, Response, json
from ast import literal_eval
import ast

# Connect to graph
authenticate("localhost:7474",'neo4j','test123')
graph = Graph('http://localhost:7474/db/data/')

# Reading in computed similarity values
similarity_db = pd.read_csv('u.similarity', sep='|')

# Creating Query
tx = graph.begin()
query = ("MATCH (m_ref:Movie {movie_id:{A}}) "
        "MATCH (m:Movie {movie_id:{B}}) MERGE (m_ref)-[r:`Similarity` {score: {C}}]->(m)")
for index, m in similarity_db.iterrows() :
    similarity = literal_eval(m.similarity)
    for sim in similarity:
        if sim[0] != m['id']:
            tx.run(query, {"A": m['id'], "B": sim[0], "C": sim[1]})
    tx.process()
    if index%10==0 :
        tx.commit()
        tx = graph.begin()
tx.commit()
