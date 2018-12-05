# Graph-based Recommendation System


## Installation

- Install Neo4j
  - For macOS: `brew install neo4j`
- Install Python3 virtual environment `python3 -m venv <virtual environment name>`
- Activate virtual environment `source <virtualenv name>/bin/activate`
- Install python dependencies `pip3 install -r requirements.txt`


## Graph Creation and Initial Setup

- Run Neo4j locally on post 7474.
- To create the graph `python build_graph.py`. This adds nodes for _user_, _movie_ and _genre_ and edges for _Is_genre_ and _Has_rated_.
- To create the LSA model for movie synopsis similarity `python build_model.py`. This builds the LSA model and saves information to file.
- Adding the _similarity_ edge to the graph `python add_edge.py`


## Running

- To run the Flask application `python app.py`. Server runs at port 5000.

## Collaborative Filtering approach

- Endpoint: `~/recommendations_user`
- Method: `POST`
- Input: `JSON`
  ```
  {
    user: <user id>,
    threshold: <similarity threshold>,
    count: <number of results to be returned>
  }
  ```

## Content-based Filtering approach

- Endpoint: `~/recommendations_movie`
- Method: `POST`
- Input: `JSON`
  ```
  {
    user: <user id>,
    threshold_similarity: <similarity threshold>,
    threshold_appreciation: <appreciation threshold>,
    count: <number of results to be returned>
  }
  ```

## Adding a new user

  - Endpoint: `~/add_user`
  - Method: `POST`
  - Input: `JSON`
    ```
    {
      <movie_id>: <rating>,
      .
      .
      .
      <movie_id>: <rating>
    }
    ```
