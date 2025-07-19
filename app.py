from flask import Flask, request, jsonify, send_from_directory
import requests
import os
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='static')

TMDB_API_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwMWI1M2ZjYWRmYTM2NWI4ODExMzYyY2FlMjUxNDkzNSIsIm5iZiI6MTc1MjM0MjYwMi41NDcwMDAyLCJzdWIiOiI2ODcyYTA0YTFkMGVmNzllYWI3MDRmZTgiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.7YmZs21L091OhWQx4ov5at24-NMXviEUfWeDaw1Y0uo"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

def scrape_imdb(query, media_type):
    search_url = f"https://www.imdb.com/find?q={query}&s={'tt' if media_type == 'movie' else 'tv'}"
    resp = requests.get(search_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = soup.select('.findResult .result_text a')
    output = []
    for a in results[:5]:
        title = a.text
        link = a['href']
        imdb_id = None
        if '/title/' in link:
            imdb_id = link.split('/title/')[1].split('/')[0]
        output.append({
            "title": title,
            "year": '',
            "type": media_type,
            "tmdb_id": None,
            "imdb_id": imdb_id
        })
    return output

@app.route('/search')
def search():
    query = request.args.get('query')
    media_type = request.args.get('type', 'movie')  # movie or tv
    if not query or media_type not in ['movie', 'tv']:
        return jsonify({"error": "Missing or invalid parameters"}), 400

    url = f"{TMDB_BASE_URL}/search/{media_type}"
    params = {"query": query, "include_adult": False}
    resp = requests.get(url, headers=headers, params=params)
    output = []
    if resp.status_code == 200:
        results = resp.json().get('results', [])
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
    # If TMDb fails or returns no results, fallback to scraper
    if not output:
        output = scrape_imdb(query, media_type)
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')