from neo4j import GraphDatabase
import os
import dotenv

dotenv.load_dotenv()
# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", os.getenv("NEO4j_PASSWORD"))

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Successfully connected to Neo4j.")

    # summary = driver.execute_query("""
    #     CREATE (a:Person {name: $name})
    #     CREATE (b:Person {name: $friendName})
    #     CREATE (a)-[:KNOWS]->(b)
    #     """,
    #                                name="Alice", friendName="David",
    #
    #                                ).summary
    # print("Created {nodes_created} nodes in {time} ms.".format(
    #     nodes_created=summary.counters.nodes_created,
    #     time=summary.result_available_after
    # ))

    records, summary, keys = driver.execute_query(
        """
        MATCH (p:Person{name: $name})-[r:DIRECTED]->(m:Movie)
        WHERE m.year > $year
        RETURN p.name AS director, m.year AS year, m.title AS movie
        """,
        # name="张艺谋",year=1990,
        parameters_={'name':'张艺谋', 'year':1990},
    )

    print(f"查询返回了{len(records)}条记录，运行时间为{summary.result_available_after}ms")

    for record in records:
        print(f"{record['director']}在{record['year']}年导演了《{record['movie']}》")