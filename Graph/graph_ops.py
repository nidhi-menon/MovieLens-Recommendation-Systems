from py2neo import Graph, authenticate
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, Response, json
import time


def get_recommendations_person(user_id, threshold, result_limit):
    # Connecting to Graph
    authenticate("localhost:7474",'neo4j','test123')
    graph = Graph('http://localhost:7474/db/data/')

    start_time = time.time()
    # Executing Query
    query = (
        'MATCH (m1:`Movie`)<-[:`Has_rated`]-(u1:`User` {user_id:{user_id}}) '
        'WITH count(m1) as movie_count '
        'MATCH (u2:`User`)-[r2:`Has_rated`]->(m1:`Movie`)<-[r1:`Has_rated`]-(u1:`User` {user_id:{user_id}}) '
        'WHERE (NOT u2=u1) AND (abs(r2.rating - r1.rating) <= 1) '
        'WITH u1, u2, tofloat(count(DISTINCT m1))/movie_count as similarity '
        'WHERE similarity>{threshold} '
        'MATCH (m:`Movie`)<-[r:`Has_rated`]-(u2) '
        'WHERE (NOT (m)<-[:`Has_rated`]-(u1)) '
        'WITH DISTINCT m, count(r) as number_of_users, tofloat(sum(r.rating)) as sum_ratings '
        'WHERE number_of_users > 1 '
        'RETURN m, sum_ratings/number_of_users as score ORDER BY score DESC LIMIT {result_limit}'
        )
    tx = graph.begin()
    cursor = tx.run(query, {'user_id': user_id, 'threshold': threshold, 'result_limit': result_limit})
    tx.commit()
    end_time = time.time()
    print("\n\n Time = ")
    print(end_time-start_time)
    print("\n\n")

    # Curating result object
    result = list()
    for i in cursor:
        entry = json.dumps(i[0])
        entry = json.loads(entry)
        entry['similarity'] = i[1]
        result.append(entry)

    # Returning the result
    return json.dumps(result)

def add_user(data):
    try:
        # Connecting to Graph
        authenticate("localhost:7474",'neo4j','test123')
        graph = Graph('http://localhost:7474/db/data/')

        # Getting the number of users
        query = ('MATCH(n:User) RETURN COUNT(n)')
        result = graph.run(query)
        for i in result:
            count = int(json.dumps(i[0]))
            break

        # Determining the new user id
        new_user_id = count + 1

        print("\n\n")
        print(new_user_id)
        print("\n\n")

        # Creating a DSV file
        file = open("new_user.data", "w")
        for key in data:
            entry = "%s|%s\n" % (int(key), int(data[key]))
            file.write(entry)
        file.close()

        # Adding to DB
        tx = graph.begin()
        query = "MERGE (a:`User`{user_id:{A}}) RETURN a"
        tx.run(query, {"A": new_user_id})
        tx.commit()

        ratings = pd.read_csv('new_user.data', sep='|', header=None, names=['item_id', 'rating'])

        # Create Has_rated relations between new user and movies
        tx = graph.begin()
        query = ("MATCH (u:`User`{user_id:{A}}) "
                   "MATCH (m:`Movie`{movie_id:{C}}) MERGE (u)-[r:`Has_rated`{rating:{B}}]->(m) RETURN r")
        count = 0
        for r,row in ratings.iterrows() :
          tx.run(query, {"A": new_user_id, "B": int(row.loc['rating']), "C": int(row.loc['item_id'])})
          count+=1
          if count%100 == 0:
              tx.process()
        tx.commit()
        return Response("Added new user with ID = " + str(new_user_id), status=201, mimetype='application/json')
    except:
        return Response("User could not be added", status=500, mimetype='application/json')


def get_recommendations_movie(user_id, threshold_appreciated, threshold_similar, result_limit):
    # Connecting to Graph
    authenticate("localhost:7474",'neo4j','test123')
    graph = Graph('http://localhost:7474/db/data/')

    # Executing the query
    query = ('MATCH (user:User {user_id:{user_id}}) '
        'MATCH (unwatched:Movie) '
        'WHERE NOT ((user)-[:Has_rated]->(unwatched)) '
        'WITH collect(unwatched.movie_id) as unwatched_set, user '
        'MATCH (user)-[rate:Has_rated]->(appreciated:Movie) '
        'WHERE rate.rating > {threshold_appreciated} '
        'MATCH (appreciated)-[sim:Similarity]-(reco:Movie) '
        'WHERE reco.movie_id in unwatched_set and sim.score > {threshold_similar} '
        'WITH collect(reco.movie_id) as reco_set, user, sim, reco '
        'MATCH (users:User)-[r:Has_rated]->(m:Movie) '
        'Where m.movie_id in reco_set '
        'RETURN distinct reco.movie_id as movie_id, reco.title, sum(sim.score)*avg(r.rating) as score '
        'ORDER BY score DESC LIMIT {result_limit}')

    tx = graph.begin()
    cursor=tx.run(query, {"user_id":user_id, "threshold_appreciated":threshold_appreciated, "threshold_similar":threshold_similar, "result_limit":result_limit})
    tx.commit()

    # Constructing response
    result = list()
    for i in cursor:
        entry = json.dumps(i)
        entry = json.loads(entry)

        result.append({
            "id": entry[0],
            "title": entry[1],
            "score": entry[2]
        })

    return json.dumps(result)





if __name__ == '__main__':
    data = {"1":1,"2":2,"3":3}
    add_user(data)
