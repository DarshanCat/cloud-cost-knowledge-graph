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

def search_services(query):

    query_embedding = model.encode(query)

    with driver.session(database="neo4j") as session:
        result = session.run("MATCH (s:Service) RETURN s.name AS name, s.embedding AS embedding")

        scores = []

        for record in result:
            service_name = record["name"]
            service_embedding = np.array(record["embedding"])

            score = cosine_similarity(query_embedding, service_embedding)
            scores.append((service_name, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:5]

if __name__ == "__main__":
    user_query = input("Enter your query: ")
    results = search_services(user_query)

    print("\nTop Matching Services:")
    for name, score in results:
        print(f"{name} -> Similarity: {score:.4f}")

driver.close()
