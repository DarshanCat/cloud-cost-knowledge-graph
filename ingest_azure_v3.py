import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

AZURE_FILE = "focusazure_anon_transformed.xls"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

df = pd.read_excel(AZURE_FILE)

# OPTIONAL: limit for testing
df = df.head(100)


def insert_row(tx, row):

    cost_id = "AZURE_" + str(row.name)

    # ---------------------------
    # Core Cost Fields (LOWERCASE FIX)
    # ---------------------------
    billed_cost = float(row.get("billedcost", 0) or 0)
    currency = str(row.get("billingcurrency", "USD"))

    # ---------------------------
    # Service (FIXED LOWERCASE)
    # ---------------------------
    service_name = str(row.get("servicename", "Unknown"))
    service_category = str(row.get("servicecategory", service_name))

    # ---------------------------
    # Resource
    # ---------------------------
    resource_id = "AZURE_" + str(row.get("resourceid", cost_id))
    resource_name = str(row.get("resourcename", "Unknown"))
    resource_type = str(row.get("resourcetype", "Unknown"))

    # ---------------------------
    # Location
    # ---------------------------
    region_id = str(row.get("regionid", "Unknown"))
    region_name = str(row.get("regionname", "Unknown"))

    # ---------------------------
    # Charge
    # ---------------------------
    charge_category = str(row.get("chargecategory", "Usage"))
    charge_class = str(row.get("chargeclass", "Unknown"))

    # ---------------------------
    # Account
    # ---------------------------
    billing_account_id = "AZURE_" + str(row.get("billingaccountid", "A1"))

    # ---------------------------
    # TimeFrame
    # ---------------------------
    billing_period_start = str(row.get("billingperiodstart"))
    billing_period_end = str(row.get("billingperiodend"))

    # ---------------------------
    # Neo4j Write
    # ---------------------------
    tx.run("""
        MERGE (a:Account {billingAccountId:$billing_account_id})

        MERGE (s:Service {serviceName:$service_name})
        SET s.serviceCategory = $service_category

        MERGE (r:Resource {resourceId:$resource_id})
        SET r.resourceName = $resource_name,
            r.resourceType = $resource_type

        MERGE (l:Location {regionId:$region_id})
        SET l.regionName = $region_name

        MERGE (ch:Charge {chargeCategory:$charge_category})
        SET ch.chargeClass = $charge_class

        MERGE (t:TimeFrame {billingPeriodStart:$billing_period_start})
        SET t.billingPeriodEnd = $billing_period_end

        MERGE (v:VendorSpecificAttributes {vendorKey:$resource_id})
        SET v.vendorType = "Azure"

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
    """,
    billing_account_id=billing_account_id,
    service_name=service_name,
    service_category=service_category,
    resource_id=resource_id,
    resource_name=resource_name,
    resource_type=resource_type,
    region_id=region_id,
    region_name=region_name,
    charge_category=charge_category,
    charge_class=charge_class,
    billing_period_start=billing_period_start,
    billing_period_end=billing_period_end,
    cost_id=cost_id,
    billed_cost=billed_cost,
    currency=currency
    )


with driver.session(database="neo4j") as session:
    for _, row in df.iterrows():
        session.execute_write(insert_row, row)

print("Azure ingestion complete.")

driver.close()