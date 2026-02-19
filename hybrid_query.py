from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_best_service(query):

    query_embedding = model.encode(query)

    with driver.session(database="neo4j") as session:
        result = session.run(
            "MATCH (s:Service) RETURN s.name AS name, s.embedding AS embedding"
        )

        best_match = None
        best_score = -1

        for record in result:
            name = record["name"]
            embedding = np.array(record["embedding"])
            score = cosine_similarity(query_embedding, embedding)

            if score > best_score:
                best_score = score
                best_match = name

        return best_match

def get_cost_data(service_name):

    with driver.session(database="neo4j") as session:
        result = session.run("""
            MATCH (c:CostRecord)-[:INCURRED_BY]->(r:Resource)-[:USES_SERVICE]->(s:Service {name:$name})
            RETURN s.name AS service, SUM(c.billedCost) AS total_cost, COUNT(c) AS records
        """, name=service_name)

        return result.single()

if __name__ == "__main__":
    user_query = input("Ask about cloud cost: ")

    best_service = find_best_service(user_query)
    print(f"\nMost relevant service: {best_service}")

    data = get_cost_data(best_service)

    if data:
        print("\n--- AI Response ---")
        print(f"The total cost for {data['service']} is ${data['total_cost']} "
              f"across {data['records']} billing records.")
    else:
        print("No data found.")

driver.close()
