from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "Test1234")
)

with driver.session(database="neo4j") as session:
    result = session.run("RETURN 1 AS num")
    print(result.single()["num"])

driver.close()
