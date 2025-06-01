import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('TMDB_API_KEY')
def get_tmdb_movie_metadata(title, director_name, api_key, year=None):
    # 1. 제목(및 연도)으로 영화 후보 검색
    search_url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": api_key,
        "query": title
    }
    if year:
        params["primary_release_year"] = year
    resp = requests.get(search_url, params=params)
    data = resp.json()
    if not data.get("results"):
        print(f"[TMDB] '{title}' not found.")
        return None

    # 2. 후보 영화들 중 감독명이 일치하는 영화 찾기
    for movie in data["results"]:
        movie_id = movie["id"]
        # 크레딧에서 감독 추출
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
        credits_resp = requests.get(credits_url, params={"api_key": api_key})
        credits_data = credits_resp.json()
        directors = [crew['name'] for crew in credits_data.get('crew', []) if crew.get('job') == 'Director']
        if director_name in directors:
            # 상세 정보, 키워드 등 추가 조회
            detail_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            detail_params = {"api_key": api_key, "language": "en-US"}
            detail_resp = requests.get(detail_url, params=detail_params)
            detail_data = detail_resp.json()

            keywords_url = f"https://api.themoviedb.org/3/movie/{movie_id}/keywords"
            keywords_resp = requests.get(keywords_url, params={"api_key": api_key})
            keywords_data = keywords_resp.json()
            keywords = [kw['name'] for kw in keywords_data.get('keywords', [])]

            actors = [cast['name'] for cast in credits_data.get('cast', [])[:5]]

            return {
                "title": detail_data.get("title", ""),
                "vote_average": detail_data.get("vote_average", 0.0),
                "vote_count": detail_data.get("vote_count", 0),
                "release_date": detail_data.get("release_date", ""),
                "overview": detail_data.get("overview", ""),
                "genres": detail_data.get("genres", []),
                "production_companies": detail_data.get("production_companies", []),
                "keywords": keywords,
                "actors": actors,
                "directors": directors
            }
    print(f"[TMDB] No '{title}' found with director '{director_name}'.")
    return None

# 사용 예시
if __name__ == "__main__":
    api_key = os.getenv('TMDB_API_KEY')
    meta = get_tmdb_movie_metadata("Dunkirk", "Christopher Nolan", api_key, year=2017)
    print(meta)