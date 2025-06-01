import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from modules.Get_metadata_TMDB import get_tmdb_movie_metadata
driver = GraphDatabase.driver("bolt://localhost:7687", auth=('neo4j', 'park0923'))

load_dotenv()
load_dotenv()
api_key = os.getenv('TMDB_API_KEY')
def find_movie_node(tx, movie_title, threshold=0.7):
    """
    Find movie node in neo4j Database
    :param tx:
    :param movie_title:
    :param threshold:
    :return: Node or None
    """
    result = tx.run("""
    MATCH (m:Movie)
    WHERE toLower(m.title) = toLower($movie_title)
    RETURN m AS node, 1.0 AS score
    LIMIT 1
    """, movie_title=movie_title)
    record = result.single()
    if record:
        print(f"[SYSTEM] MOVIE {movie_title} FOUND (exact match)")
        return record['node']

    result = tx.run("""
    CALL db.index.fulltext.queryNodes("movieTitleIndex", $movie_title)
    YIELD node, score
    RETURN node, score
    ORDER BY score DESC LIMIT 1
    """, movie_title=movie_title)
    record = result.single()
    if record and record['score'] >= threshold:
        print(f"[SYSTEM] MOVIE {movie_title} HAS FOUND")
        return record['node']
    else:
        print(f"[SYSTEM] MOVIE {movie_title} HAS NOT FOUND, START SEARCHING...")
        return None


def create_new_movie(driver, metadata, database):
    with driver.session(database=database) as session:
        session.run(
            """
            MERGE (m:Movie {title: $title})
            SET m.overview = $overview,
            m.vote_average = $vote_average,
            m.vote_count = $vote_count,
            m.release_date = $release_date
            """,
            title=metadata['title'], overview=metadata['overview'],
            vote_average=metadata['vote_average'], vote_count=metadata['vote_count'],
            release_date=metadata['release_date']
        )

        for genre in metadata.get('genres', []):
            session.run(
                """
                MERGE (g:Genre {name: $genre})
                MERGE (m:Movie {title: $title})
                MERGE (m)-[:HAS_GENRE]->(g)
                """,
                genre=genre['name'], title=metadata['title']
            )

        for keyword in metadata.get('keywords', []):
            session.run(
                """
                MERGE (k:Keyword {name: $keyword})
                MERGE (m:Movie {title: $title})
                MERGE (m)-[:HAS_KEYWORD]->(k)
                """,
                keyword=keyword, title=metadata['title']
            )

        for production in metadata.get('production_companies', []):
            session.run(
                """
                MERGE (p:Production {name: $production})
                MERGE (m:Movie {title: $title})
                MERGE (m)-[:PRODUCED_BY]->(p)
                """,
                production=production['name'], title=metadata['title']
            )

        create_and_link_actors(driver, metadata['title'], metadata['actors'], database)
        create_and_link_director(driver, metadata['title'], metadata['directors'], database)

        print(f"CREATED: {metadata['title']}")
def create_and_link_actors(driver, movie_title, actors, database):
    if isinstance(actors, str):
        actors = [a.strip() for a in actors.split(',') if a.strip()]
    elif not isinstance(actors, list):
        actors = [actors]
    with driver.session(database=database) as session:
        for actor in actors:
            session.run(
                """
                MERGE (a:Actor {name: $actor})
                MERGE (m:Movie {title: $title})
                MERGE (a)-[:ACTED_IN]->(m)
                """, actor=actor, title=movie_title
            )
            print(f"[UPDATE] Updated {movie_title} with {actor}")


def create_and_link_director(driver, movie_title, directors, database):
    if isinstance(directors, str):
        directors = [d.strip() for d in directors.split(',') if d.strip()]
    elif not isinstance(directors, list):
        directors = [directors]
    with driver.session(database=database) as session:
        for director in directors:
            session.run(
                """
                MERGE (d:Director {name: $director})
                MERGE (m:Movie {title: $title})
                MERGE (d)-[:DIRECTED]->(m)
                """, director=director, title=movie_title
            )
            print(f"[UPDATE] Updated {movie_title} with {director}")


def update_nodes(movie_data, database, tmdb_api_key=api_key):
    for entry in movie_data:
        with driver.session(database=database) as session:
            movie_node = session.execute_read(find_movie_node, entry['title'])
        if not movie_node:
            metadata = get_tmdb_movie_metadata(entry['title'], entry['director'], tmdb_api_key)
            if metadata:
                create_new_movie(driver, metadata, database)
            else:
                print(f"[ERROR] TMDB metadata not found for {entry['title']}")
                continue
        create_and_link_actors(driver, entry['title'], entry.get('actors', []), database)
        create_and_link_director(driver, entry['title'], entry.get('director', []), database)

# if __name__ == "__main__":
#     # driver = GraphDatabase.driver("bolt://localhost:7687", auth=('neo4j', 'park0923'))
#     test_movie_title = "Inception"
#     test_actors = ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Ellen Page"]
#     test_director = "Christopher Nolan"
#     create_and_link_actors(driver, test_movie_title, test_actors, database="test")
#     create_and_link_director(driver, test_movie_title, test_director, database="test")
