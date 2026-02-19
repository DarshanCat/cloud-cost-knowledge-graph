from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_services(tx):
    result = tx.run("MATCH (s:Service) RETURN s.name AS name")
    services = [record["name"] for record in result]

    for service in services:
        embedding = model.encode(service).tolist()

        tx.run("""
            MATCH (s:Service {name: $name})
            SET s.embedding = $embedding
        """, name=service, embedding=embedding)

with driver.session(database="neo4j") as session:
    session.execute_write(embed_services)

print("Service embeddings added successfully!")

driver.close()
