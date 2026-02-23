import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

AWS_FILE = "aws_test-focus-00001.snappy_transformed.xls"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

df = pd.read_excel(AWS_FILE)
df = df.head(50)  # start small for testing


def insert_row(tx, row):

    cost_id = str(row.name)

    billed_cost = float(row.get("billedCost", 0))
    currency = str(row.get("currency", "USD"))
    service_name = str(row.get("serviceName", "Unknown"))
    resource_id = str(row.get("resourceId", row.name))
    region = str(row.get("regionName", "Unknown"))
    charge_category = str(row.get("chargeCategory", "Usage"))
    billing_account = str(row.get("billingAccountId", "A1"))

    tx.run("""
        MERGE (a:Account {billingAccountId:$billing_account})

        MERGE (s:Service {serviceName:$service_name})

        MERGE (r:Resource {resourceId:$resource_id})
        MERGE (l:Location {regionId:$region})

        MERGE (ch:Charge {chargeCategory:$charge_category})

        MERGE (t:TimeFrame {billingPeriodStart:"2026-01-01"})
        SET t.billingPeriodEnd = "2026-01-31"

        MERGE (v:VendorSpecificAttributes {vendorKey:$cost_id})
        SET v.vendorType = "AWS"

        MERGE (ca:CostAllocation {allocationRuleName:"DefaultRule"})
        SET ca.allocationMethod = "EvenSplit",
            ca.isSharedCost = false

        MERGE (c:CostRecord {costRecordId:$cost_id})
        SET c.billedCost = $billed_cost,
            c.currency = $currency,
            c.effectiveCost = $billed_cost

        MERGE (c)-[:BELONGS_TO_BILLING_ACCOUNT]->(a)
        MERGE (c)-[:HAS_CHARGE]->(ch)
        MERGE (c)-[:HAS_TIMEFRAME]->(t)
        MERGE (c)-[:INCURRED_BY]->(r)
        MERGE (r)-[:USES_SERVICE]->(s)
        MERGE (r)-[:DEPLOYED_IN]->(l)
        MERGE (c)-[:HAS_VENDOR_ATTRS]->(v)
        MERGE (c)-[:ALLOCATED_VIA]->(ca)
    """,
    cost_id=cost_id,
    billed_cost=billed_cost,
    currency=currency,
    service_name=service_name,
    resource_id=resource_id,
    region=region,
    charge_category=charge_category,
    billing_account=billing_account
    )


with driver.session(database="neo4j") as session:
    for _, row in df.iterrows():
        session.execute_write(insert_row, row)

print("Ingestion v2 complete.")

driver.close()