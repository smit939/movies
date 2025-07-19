from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__)

TMDB_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMWI1M2ZjYWRmYTM2NWI4ODExMzYyY2FlMjUxNDkzNSIsIm5iZiI6MTc1MjM0MjYwMi41NDcwMDAyLCJzdWIiOiI2ODcyYTA0YTFkMGVmNzllYWI3MDRmZTgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.7YmZs21L091OhWQx4ov5at24-NMXviEUfWeDaw1Y0uo"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    media_type = request.args.get('type', 'movie')  # movie or tv
    if not query or media_type not in ['movie', 'tv']:
        return jsonify({"error": "Missing or invalid parameters"}), 400

    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {"query": query, "include_adult": False}
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        return jsonify({"error": "TMDb API error"}), 500
    results = resp.json().get('results', [])
    output = []
    for item in results:
        tmdb_id = item.get('id')
        title = item.get('title') if media_type == 'movie' else item.get('name')
        year = (item.get('release_date') or item.get('first_air_date') or '')[:4]
        imdb_id = None
        # Get IMDb ID
        details_url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}"
        details_resp = requests.get(details_url, headers=headers)
        if details_resp.status_code == 200:
            imdb_id = details_resp.json().get('imdb_id')
        output.append({
            "title": title,
            "year": year,
            "type": media_type,
            "tmdb_id": tmdb_id,
            "imdb_id": imdb_id
        })
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')