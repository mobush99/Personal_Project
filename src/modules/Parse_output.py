import re

def parse_output(text):

    results = []
    pattern = r"<m>(.*?)</m>:\s*<a>(.*?)</a>\s*<d>(.*?)</d>"
    matches = re.findall(pattern, text, re.DOTALL)
    if '<m>' not in text:
        return None

    for movie, actors, directors in matches:
        actor_list = [a.strip() for a in actors.split(',') if a.strip()]
        director_list = [d.strip() for d in directors.split(',') if d.strip()]
        results.append({
            "movie": movie.strip(),
            "actors": actor_list,
            "directors": director_list
        })
    return results

def JSON_parse_output(text):
    results = []
    movies = text.get('Movies', [])
    if not movies:
        return None

    for movie in movies:
        title = movie.get('title', '').strip()
        actors = movie.get('actors', [])
        if isinstance(actors, str):
            actor_list = [a.strip() for a in actors.split(',') if a.strip()]
        else:
            actor_list = [a.strip() for a in actors if a.strip()]

        director = movie.get('director', '').strip()

        results.append({
            'title': title,
            'actors': actor_list,
            'director': director
        })

    return results
