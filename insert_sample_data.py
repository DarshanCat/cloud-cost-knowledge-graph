from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt://127.0.0.1:7687",
    auth=("neo4j", "Test1234")
)


def insert_data(tx):
    tx.run("""
        MERGE (a:Account {id: 'A1', name: 'Main Account'})
        MERGE (s:Service {name: 'EC2', category: 'Compute'})
        MERGE (r:Resource {id: 'R1', name: 'EC2-Instance-1', type: 'VM'})
        MERGE (l:Location {region: 'us-east-1'})

        MERGE (r)-[:USES_SERVICE]->(s)
        MERGE (r)-[:DEPLOYED_IN]->(l)

        MERGE (c:CostRecord {id: 'C1', billedCost: 100, currency: 'USD'})
        MERGE (c)-[:BELONGS_TO]->(a)
        MERGE (c)-[:INCURRED_BY]->(r)
    """)


with driver.session(database="neo4j") as session:
    session.execute_write(insert_data)

print("Sample Data Inserted Successfully")

driver.close()

