from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_nodes(label, text_query):

    with driver.session(database="neo4j") as session:
        result = session.run(text_query)

        for record in result:
            node_id = record["id"]
            text = record["text"]

            if text is None:
                continue

            embedding = model.encode(text).tolist()

            session.run(
                f"""
                MATCH (n:{label}) WHERE id(n) = $node_id
                SET n.embedding = $embedding
                """,
                node_id=node_id,
                embedding=embedding
            )


# ---- Service ----
embed_nodes("Service",
    "MATCH (s:Service) RETURN id(s) AS id, "
    "'Service ' + s.serviceName AS text"
)

# ---- Resource ----
embed_nodes("Resource",
    "MATCH (r:Resource) RETURN id(r) AS id, "
    "'Resource ' + r.resourceId AS text"
)

# ---- Charge ----
embed_nodes("Charge",
    "MATCH (c:Charge) RETURN id(c) AS id, "
    "'Charge category ' + c.chargeCategory AS text"
)

# ---- Vendor ----
embed_nodes("VendorSpecificAttributes",
    "MATCH (v:VendorSpecificAttributes) RETURN id(v) AS id, "
    "'Vendor type ' + v.vendorType AS text"
)

# ---- CostAllocation ----
embed_nodes("CostAllocation",
    "MATCH (ca:CostAllocation) RETURN id(ca) AS id, "
    "'Allocation method ' + ca.allocationMethod AS text"
)

# ---- CostRecord ----
embed_nodes("CostRecord",
    "MATCH (c:CostRecord) RETURN id(c) AS id, "
    "'CostRecord billedCost ' + toString(c.billedCost) AS text"
)

print("Embeddings v2 added successfully.")

driver.close()