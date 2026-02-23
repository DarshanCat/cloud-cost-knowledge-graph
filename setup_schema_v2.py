from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def create_constraints(tx):
    # -------- Core Entity Uniqueness --------
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:CostRecord) REQUIRE c.costRecordId IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Account) REQUIRE a.billingAccountId IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Service) REQUIRE s.serviceName IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Resource) REQUIRE r.resourceId IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.regionId IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (ch:Charge) REQUIRE ch.chargeCategory IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (t:TimeFrame) REQUIRE t.billingPeriodStart IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (v:VendorSpecificAttributes) REQUIRE v.vendorKey IS UNIQUE")
    tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (ca:CostAllocation) REQUIRE ca.allocationRuleName IS UNIQUE")

def create_indexes(tx):
    # -------- Performance Indexes --------
    tx.run("CREATE INDEX IF NOT EXISTS FOR (c:CostRecord) ON (c.billedCost)")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (s:Service) ON (s.serviceCategory)")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (r:Resource) ON (r.resourceType)")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (ch:Charge) ON (ch.chargeClass)")
    tx.run("CREATE INDEX IF NOT EXISTS FOR (ca:CostAllocation) ON (ca.allocationMethod)")

with driver.session(database="neo4j") as session:
    session.execute_write(create_constraints)
    session.execute_write(create_indexes)

print("Schema v2 created successfully.")

driver.close()