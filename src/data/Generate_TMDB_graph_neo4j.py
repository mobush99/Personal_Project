import pandas as pd
from neo4j import GraphDatabase
from tqdm import tqdm
"""
>> title | vote_average | vote_count | release_date | overview | genres | production_companies | keywords
"""

"""
1. Creating Nodes on Neo4j GraphDB
"""
def create_movie(tx, title, overview, vote_average, vote_count, release_date):
    tx.run("""
        MERGE (m:Movie {title: $title})
        SET m.overview = $overview,
        m.vote_average = $vote_average,
        m.vote_count = $vote_count,
        m.release_date = $release_date
    """, title=title, overview=overview, vote_average=vote_average, vote_count=vote_count, release_date=release_date)

def create_genre(tx, genre):
    tx.run("MERGE (g:Genre {name: $genre})", genre=genre)

def create_keyword(tx, keyword):
    tx.run("MERGE (k:Keyword {name: $keyword})", keyword=keyword)

def create_production(tx, production):
    tx.run("MERGE (p:Production {name: $production})", production=production)

"""
2. Creating Edges(Connections/Relations) on Neo4j GraphDB
"""
def link_movie_genre(tx, title, genre):
    tx.run("""
        MATCH (m:Movie {title: $title}), (g:Genre {name: $genre})
        MERGE (m)-[:HAS_GENRE]->(g)
    """, title=title, genre=genre)

def link_movie_keyword(tx, title, keyword):
    tx.run("""
        MATCH (m:Movie {title: $title}), (k:Keyword {name: $keyword})
        MERGE (m)-[:HAS_KEYWORD]->(k)
    """, title=title, keyword=keyword)

def link_movie_production(tx, title, production):
    tx.run("""
        MATCH (m:Movie {title: $title}), (p:Production {name: $production})
        MERGE (m)-[:PRODUCED_BY]->(p)
    """, title=title, production=production)


"""
3. Load Data to Neo4j GraphDB
"""
def to_neo4j(df, driver):
    with driver.session() as session:
        for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
            # Creating Movie Nodes
            session.execute_write(
                create_movie, row['title'], row['overview'], row['vote_average'],
                row['vote_count'], row['release_date']
            )
            # Create Genre Nodes & Link
            for genre in row['genres']:
                if genre:
                    session.execute_write(create_genre, genre)
                    session.execute_write(link_movie_genre, row['title'], genre)
            # Create Keyword Nodes & Link
            for keyword in row['keywords']:
                if keyword:
                    session.execute_write(create_keyword, keyword)
                    session.execute_write(link_movie_keyword, row['title'], keyword)
            # Create Production Nodes & Link
            for production in row['production_companies']:
                if production:
                    session.execute_write(create_production, production)
                    session.execute_write(link_movie_production, row['title'], production)
    driver.close()
    print("Loading TMDB Data to Neo4j ... FINISHED")

def neo4j_test_node(df, driver, n=5):
    with driver.session(database="test") as session:
        for idx, row in tqdm(df.head(n).iterrows(), total=n):
            # Creating Movie Nodes
            session.execute_write(
                create_movie, row['title'], row['overview'], row['vote_average'],
                row['vote_count'], row['release_date']
            )
            # Create Genre Nodes & Link
            for genre in row['genres']:
                if genre:
                    session.execute_write(create_genre, genre)
                    session.execute_write(link_movie_genre, row['title'], genre)
            # Create Keyword Nodes & Link
            for keyword in row['keywords']:
                if keyword:
                    session.execute_write(create_keyword, keyword)
                    session.execute_write(link_movie_keyword, row['title'], keyword)
            # Create Production Nodes & Link
            for production in row['production_companies']:
                if production:
                    session.execute_write(create_production, production)
                    session.execute_write(link_movie_production, row['title'], production)
    driver.close()
    print(f"Test Session: Creating {n} Nodes ... FINISHED")

if __name__ == '__main__':
    df = pd.read_pickle('../data/TMDB_movie_dataset.pkl')
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'park0923'))
    # to_neo4j(df, driver)
    neo4j_test_node(df, driver, n=5)



