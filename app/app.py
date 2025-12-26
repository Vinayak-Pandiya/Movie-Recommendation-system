import pickle
import requests
from flask import Flask, jsonify, request, send_from_directory
import os

app = Flask(__name__, static_folder='static', static_url_path='')

try:
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    movie_list = movies['title'].values
except FileNotFoundError as e:
    movies = None
    similarity = None
    movie_list = []


def fetch_poster(movie_id):
    try:
        url = (
            "https://api.themoviedb.org/3/movie/{}"
            "?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        ).format(movie_id)
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        return None
    except:
        return None


def recommend(movie):
    if movies is None or similarity is None:
        return [], []
    
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1],
    )

    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:10]:
        try:
            movie_id = movies.iloc[i[0]].movie_id
            poster = fetch_poster(movie_id)
            if poster: 
                recommended_movie_posters.append(poster)
                recommended_movie_names.append(movies.iloc[i[0]].title)
        except:
            continue

    return recommended_movie_names, recommended_movie_posters


@app.route("/")
def index():
    return send_from_directory('static', 'index.html')


@app.route("/api/movies")
def list_movies():
    return jsonify({"titles": list(movie_list)})


@app.route("/api/recommend", methods=["POST"])
def recommend_api():
    data = request.get_json()
    title = data.get("title")
    
    if not title:
        return jsonify({"error": "title is required"}), 400
    
    if movies is None:
        return jsonify({"error": "Model not loaded"}), 500
    
    if title not in movies["title"].values:
        return jsonify({"error": "Movie not found"}), 404

    names, posters = recommend(title)

    results = []
    for name, poster in zip(names, posters):
        results.append({
            "title": name,
            "poster_url": poster
        })

    return jsonify({
        "base_title": title, 
        "recommendations": results
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
