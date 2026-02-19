import pandas as pd
from neo4j import GraphDatabase

# ----------- CONFIG -----------
AWS_FILE = "aws_test-focus-00001.snappy_transformed.xls"
URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"
# --------------------------------

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Load Excel
df = pd.read_excel(AWS_FILE)

# Take only first 50 rows for testing
df = df.head(50)


def insert_row(tx, row):
    cost_id = str(row.get("lineItemId", row.name))
    service_name = str(row.get("serviceName", "Unknown"))
    resource_id = str(row.get("resourceId", row.name))
    region = str(row.get("regionName", "Unknown"))
    billed_cost = float(row.get("billedCost", 0))
    currency = str(row.get("currency", "USD"))

    tx.run("""
        MERGE (s:Service {name: $service_name})
        MERGE (r:Resource {id: $resource_id})
        MERGE (l:Location {region: $region})
        MERGE (c:CostRecord {id: $cost_id})

        SET c.billedCost = $billed_cost,
            c.currency = $currency

        MERGE (r)-[:USES_SERVICE]->(s)
        MERGE (r)-[:DEPLOYED_IN]->(l)
        MERGE (c)-[:INCURRED_BY]->(r)
    """,
           service_name=service_name,
           resource_id=resource_id,
           region=region,
           cost_id=cost_id,
           billed_cost=billed_cost,
           currency=currency
           )


with driver.session(database="neo4j") as session:
    for _, row in df.iterrows():
        session.execute_write(insert_row, row)

print("Excel Data Inserted Successfully!")

driver.close()
