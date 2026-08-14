#!/usr/bin/env python3
"""
Fetch movies from TMDb and filter by budget only.

Filter:
  - Budget >= $100,000,000 (regardless of rating)
  - Released this year up to today

Output:
  - filtered_movies_radarr.json    (StevenLu Custom format: title + imdb_id)

Required environment variable:
  TMDB_API_KEY - Your TMDb API Read Access Token (starts with "eyJ...")
"""

import requests
import json
import os
import sys
import time
from datetime import datetime

# Short-lived script: init must be paired with an explicit flush() before
# exit, otherwise events queued in the background worker are lost when the
# process ends.


# ===== CONFIGURATION =====

API_KEY = os.environ.get("TMDB_API_KEY")
if not API_KEY:
    print("ERROR: Environment variable TMDB_API_KEY is not set.")
    sys.exit(1)

OUTPUT_FILE = "filtered_movies_radarr.json"
MIN_BUDGET = 100_000_000  # $100M

BASE_URL = "https://api.themoviedb.org/3"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


# ===== FUNCTIONS =====

def get_movie_ids(pages=10):
    """Fetch movie IDs from TMDb. Only this year up to today."""
    movie_ids = set()
    current_year = datetime.now().year
    today_str = datetime.now().strftime("%Y-%m-%d")
    start_date_str = f"{current_year}-01-01"

    endpoints = ["/movie/now_playing"]
    discover_endpoints = [
        f"/discover/movie?sort_by=popularity.desc&primary_release_date.gte={start_date_str}&primary_release_date.lte={today_str}",
        f"/discover/movie?sort_by=vote_count.desc&primary_release_date.gte={start_date_str}&primary_release_date.lte={today_str}",
        f"/discover/movie?sort_by=revenue.desc&primary_release_date.gte={start_date_str}&primary_release_date.lte={today_str}",
    ]

    for endpoint in endpoints + discover_endpoints:
        for page in range(1, pages + 1):
            url = f"{BASE_URL}{endpoint}{'&' if '?' in endpoint else '?'}page={page}"
            try:
                response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code == 429:
                    time.sleep(2)
                    response = requests.get(url, headers=HEADERS, timeout=30)
                if response.status_code == 401:
                    sys.exit(
                        "ERROR: TMDb avvisade nyckeln (401). TMDB_API_KEY ska vara "
                        "ett API Read Access Token (börjar med 'eyJ'), inte en v3-API-nyckel."
                    )
                if response.status_code == 200:
                    for movie in response.json().get("results", []):
                        if endpoint in endpoints:
                            rd = movie.get("release_date", "")
                            if not rd or rd < start_date_str or rd > today_str:
                                continue
                        movie_ids.add(movie["id"])
                else:
                    print(f"  Varning: {response.status_code} för {url}", file=sys.stderr)
            except Exception as e:
                print(f"  Varning: {e}", file=sys.stderr)
                time.sleep(1)

    return list(movie_ids)


def simplify_movie_stevenlu(movie):
    """Create a StevenLu-compatible movie object (title + imdb_id)."""
    imdb_id = movie.get("imdb_id")
    if not imdb_id:
        return None
    return {
        "title": movie.get("title"),
        "imdb_id": imdb_id
    }


def fetch_and_filter_movies(movie_ids):
    """Fetch details and keep only big budget movies from this year."""
    filtered = []
    skipped_no_imdb = 0
    current_year = datetime.now().year
    today_str = datetime.now().strftime("%Y-%m-%d")
    start_date_str = f"{current_year}-01-01"

    for i, movie_id in enumerate(movie_ids):
        if i % 100 == 0:
            print(f"  Processing movie {i+1}/{len(movie_ids)}...")

        try:
            response = requests.get(f"{BASE_URL}/movie/{movie_id}", headers=HEADERS, timeout=30)
            if response.status_code == 429:
                time.sleep(2)
                response = requests.get(f"{BASE_URL}/movie/{movie_id}", headers=HEADERS, timeout=30)
            if response.status_code != 200:
                continue

            movie = response.json()
            release_date = movie.get("release_date", "")
            if not release_date or release_date < start_date_str or release_date > today_str:
                continue

            budget = movie.get("budget", 0)
            # TMDb returns 0 for unknown/unreported budgets; skip to avoid false positives
            if budget == 0:
                continue

            if budget >= MIN_BUDGET:
                stevenlu = simplify_movie_stevenlu(movie)
                if stevenlu:
                    filtered.append(stevenlu)
                    print(f"  💰 {movie.get('title')} ({release_date}) - ${budget:,}")
                else:
                    skipped_no_imdb += 1
                    print(f"  ⚠️  {movie.get('title')} ({release_date}) - ${budget:,} [SKIPPED: No IMDb ID]")

        except Exception as e:
            print(f"  Error fetching movie {movie_id}: {e}")

    if skipped_no_imdb > 0:
        print(f"\n  ℹ️  {skipped_no_imdb} movie(s) skipped due to missing IMDb ID")

    filtered.sort(key=lambda x: x.get("title", ""))
    return filtered


def main():
    current_year = datetime.now().year
    today_str = datetime.now().strftime("%Y-%m-%d")

    print("=" * 55)
    print("BIG BUDGET MOVIES FOR RADARR (StevenLu)")
    print("=" * 55)
    print()
    print(f"Date filter:   {current_year}-01-01 to {today_str}")
    print(f"Budget filter: >= ${MIN_BUDGET:,}")
    print()

    print("Fetching movies from TMDb...")
    movie_ids = get_movie_ids(pages=10)
    print(f"Found {len(movie_ids)} movies to evaluate.\n")

    print("Filtering by budget...")
    movies = fetch_and_filter_movies(movie_ids)

    # Publicera aldrig en tom lista över en befintlig fil. Radarr/Sonarr läser
    # den här filen direkt från repot; ett tomt svar från TMDb (utgången nyckel,
    # avbrott) skulle annars tömma prenumeranternas listor tyst.
    if not movies and os.path.exists(OUTPUT_FILE):
        sys.exit(
            f"ERROR: 0 filmer efter filtrering, men {OUTPUT_FILE} finns redan. "
            "Vägrar skriva över en befintlig lista med en tom."
        )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, indent=2, ensure_ascii=False)

    print(f"\nDone!")
    print(f"  Radarr-ready: {OUTPUT_FILE}")
    print(f"  Movies found: {len(movies)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
