import pandas as pd
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

AWS_FILE = "aws_test-focus-00001.snappy_transformed.xls"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

df = pd.read_excel(AWS_FILE)
df = df.head(100)  # slightly larger sample


def insert_row(tx, row):

    cost_id = str(row.name)

    billed_cost = float(row.get("BilledCost", 0))
    currency = str(row.get("BillingCurrency", "USD"))

    service_name = str(row.get("ServiceName", "Unknown"))
    service_category = str(row.get("ServiceCategory", "Unknown"))

    resource_id = str(row.get("ResourceId", cost_id))
    resource_name = str(row.get("ResourceName", "Unknown"))
    resource_type = str(row.get("ResourceType", "Unknown"))

    region_id = str(row.get("RegionId", "Unknown"))
    region_name = str(row.get("RegionName", "Unknown"))

    charge_category = str(row.get("ChargeCategory", "Usage"))
    charge_class = str(row.get("ChargeClass", "Unknown"))
    charge_description = str(row.get("ChargeDescription", ""))

    billing_account_id = str(row.get("BillingAccountId", "A1"))
    billing_account_name = str(row.get("BillingAccountName", ""))

    billing_period_start = str(row.get("BillingPeriodStart"))
    billing_period_end = str(row.get("BillingPeriodEnd"))

    # Vendor-specific (AWS)
    x_service_code = str(row.get("x_ServiceCode", ""))
    x_usage_type = str(row.get("x_UsageType", ""))

    tx.run("""
        MERGE (a:Account {billingAccountId:$billing_account_id})
        SET a.billingAccountName = $billing_account_name

        MERGE (s:Service {serviceName:$service_name})
        SET s.serviceCategory = $service_category

        MERGE (r:Resource {resourceId:$resource_id})
        SET r.resourceName = $resource_name,
            r.resourceType = $resource_type

        MERGE (l:Location {regionId:$region_id})
        SET l.regionName = $region_name

        MERGE (ch:Charge {chargeCategory:$charge_category})
        SET ch.chargeClass = $charge_class,
            ch.chargeDescription = $charge_description

        MERGE (t:TimeFrame {billingPeriodStart:$billing_period_start})
        SET t.billingPeriodEnd = $billing_period_end

        MERGE (v:VendorSpecificAttributes {vendorKey:$resource_id})
        SET v.vendorType = "AWS",
            v.x_ServiceCode = $x_service_code,
            v.x_UsageType = $x_usage_type

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
    billing_account_name=billing_account_name,
    service_name=service_name,
    service_category=service_category,
    resource_id=resource_id,
    resource_name=resource_name,
    resource_type=resource_type,
    region_id=region_id,
    region_name=region_name,
    charge_category=charge_category,
    charge_class=charge_class,
    charge_description=charge_description,
    billing_period_start=billing_period_start,
    billing_period_end=billing_period_end,
    x_service_code=x_service_code,
    x_usage_type=x_usage_type,
    cost_id=cost_id,
    billed_cost=billed_cost,
    currency=currency
    )


with driver.session(database="neo4j") as session:
    for _, row in df.iterrows():
        session.execute_write(insert_row, row)

print("Ingestion v3 complete.")

driver.close()