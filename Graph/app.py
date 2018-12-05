from flask import Flask, request, jsonify, Response
from graph_ops import get_recommendations_movie, get_recommendations_person, add_user

app = Flask(__name__)

@app.route("/")
def hello():
    return "Welcome to Graph Based Recommendation Sytem"


@app.route("/recommendations_user", methods=['POST'])
def worker1():
    if request.method == 'POST':
        data = request.get_json()
        result = get_recommendations_person(int(data['user']), float(data['threshold']), int(data['count']))
        return Response(result, status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'message': 'API supports only POST requests'}), status=400, mimetype='application/json')

@app.route("/recommendations_movie", methods=['POST'])
def worker2():
    if request.method == 'POST':
        data = request.get_json()
        result = get_recommendations_movie(int(data['user']), float(data['threshold_appreciation']), float(data['threshold_similar']), int(data['count']))
        return Response(result, status=200, mimetype='application/json')
    else:
        return Response(json.dumps({'message': 'API supports only POST requests'}), status=400, mimetype='application/json')


@app.route("/add_user", methods=['POST'])
def new_user():
    if request.method == 'POST':
        data = request.get_json()
        return add_user(data)
    else:
        return Response(json.dumps({'message': 'API supports only POST requests'}), status=400, mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
