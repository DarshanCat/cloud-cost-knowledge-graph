from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# OPTIONAL LLM (safe mode)
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except:
    client = None

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "Test1234"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------
# INTENT DETECTION
# ---------------------------
def detect_intent(query):
    q = query.lower()

    if "compare" in q:
        return "comparison"
    elif "top" in q:
        return "ranking"
    elif "allocation" in q:
        return "allocation"
    elif "commitment" in q:
        return "commitment"
    else:
        return "cost_analysis"


# ---------------------------
# ENTITY EXTRACTION
# ---------------------------
def extract_entities(query):
    q = query.lower()

    vendors = []
    if "aws" in q:
        vendors.append("AWS")
    if "azure" in q:
        vendors.append("Azure")

    service_keyword = None
    if "storage" in q:
        service_keyword = "storage"
    elif "compute" in q:
        service_keyword = "compute"

    return {
        "vendors": vendors,
        "service_keyword": service_keyword
    }


# ---------------------------
# VECTOR SERVICE MATCH
# ---------------------------
def find_relevant_services(keyword):

    if keyword is None:
        return []

    query_embedding = model.encode(keyword)

    with driver.session(database="neo4j") as session:
        result = session.run(
            "MATCH (s:Service) WHERE s.embedding IS NOT NULL "
            "RETURN s.serviceName AS name, s.embedding AS embedding"
        )

        scored = []

        for record in result:
            name = record["name"]
            embedding = np.array(record["embedding"])

            score = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )

            scored.append((name, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in scored[:5]]


# ---------------------------
# GRAPH REASONING
# ---------------------------
def fetch_cost_data(intent, keyword, services, vendors=None):

    with driver.session(database="neo4j") as session:

        if intent == "comparison" and vendors and keyword:

            if keyword.lower() == "storage":
                concept_terms = ["storage", "blob", "disk", "file", "backup"]
            elif keyword.lower() == "compute":
                concept_terms = ["compute", "vm", "virtual", "instance"]
            else:
                concept_terms = [keyword.lower()]

            base_query = """
            MATCH (c:CostRecord)-[:INCURRED_BY]->(r:Resource)
                  -[:USES_SERVICE]->(s:Service),
                  (c)-[:HAS_VENDOR_ATTRS]->(v:VendorSpecificAttributes)
            WHERE v.vendorType IN $vendors
              AND (
            """

            conditions = []
            for i, term in enumerate(concept_terms):
                conditions.append(f"toLower(s.serviceName) CONTAINS $term{i}")

            base_query += " OR ".join(conditions)
            base_query += """
              )
              RETURN v.vendorType AS vendor,
                     s.serviceName AS service,
                     SUM(c.billedCost) AS service_cost
            """

            params = {"vendors": vendors}
            for i, term in enumerate(concept_terms):
                params[f"term{i}"] = term

            result = session.run(base_query, **params)
            return [record.data() for record in result]

        else:
            query = """
            MATCH (c:CostRecord)-[:INCURRED_BY]->(r:Resource)
                  -[:USES_SERVICE]->(s:Service)
            WHERE s.serviceName IN $services
            RETURN s.serviceName AS service,
                   SUM(c.billedCost) AS total_cost
            """

            result = session.run(query, services=services)
            return [record.data() for record in result]


# ---------------------------
# RESPONSE GENERATION
# ---------------------------
def generate_response(intent, data):

    if not data:
        return "No relevant cost data found."

    if intent == "comparison":

        response = "Cross-Cloud Storage Comparison:\n\n"

        vendor_totals = {}
        vendor_breakdown = {}

        for item in data:
            vendor = item["vendor"]
            service = item["service"]
            cost = item["service_cost"]

            vendor_totals[vendor] = vendor_totals.get(vendor, 0) + cost

            if vendor not in vendor_breakdown:
                vendor_breakdown[vendor] = []
            vendor_breakdown[vendor].append((service, cost))

        for vendor in vendor_breakdown:
            response += f"{vendor} Services:\n"
            for service, cost in vendor_breakdown[vendor]:
                response += f"  - {service}: ${cost:.2f}\n"

            response += f"  → Total: ${vendor_totals[vendor]:.2f}\n\n"

        if len(vendor_totals) == 2:
            vendors = list(vendor_totals.keys())
            diff = abs(vendor_totals[vendors[0]] - vendor_totals[vendors[1]])
            response += f"Cost Difference: ${diff:.2f}\n"

        return response

    elif intent == "ranking":
        sorted_data = sorted(data, key=lambda x: x["total_cost"], reverse=True)

        response = "Ranking Result:\n"
        for item in sorted_data:
            response += f"{item['service']} → ${item['total_cost']:.2f}\n"

        return response

    else:
        total = sum(d["total_cost"] for d in data)
        return f"Total cost across relevant services: ${total:.2f}"


# ---------------------------
# OPTIONAL LLM LAYER
# ---------------------------
def generate_llm_explanation(user_query, graph_data):

    if client is None:
        return "[LLM layer disabled - no API configured]"

    try:
        context = ""
        for item in graph_data:
            if "vendor" in item:
                context += f"{item['vendor']} - {item['service']}: ${item['service_cost']:.2f}\n"
            else:
                context += f"{item['service']}: ${item['total_cost']:.2f}\n"

        prompt = f"""
        You are a cloud cost analyst.

        User Question:
        {user_query}

        Retrieved Graph Data:
        {context}

        Provide a short professional explanation.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return "[LLM layer unavailable due to quota or API issue]"


# ---------------------------
# MAIN PIPELINE
# ---------------------------
def run_rag(query):

    intent = detect_intent(query)
    entities = extract_entities(query)

    services = find_relevant_services(entities["service_keyword"])

    data = fetch_cost_data(
        intent,
        entities["service_keyword"],
        services,
        entities["vendors"]
    )

    structured_response = generate_response(intent, data)
    llm_response = generate_llm_explanation(query, data)

    response = structured_response + "\n\nLLM Analysis:\n" + llm_response

    return {
        "intent": intent,
        "entities": entities,
        "services": services,
        "data": data,
        "response": response
    }


if __name__ == "__main__":

    user_query = input("Ask your cloud question: ")

    result = run_rag(user_query)

    print("\nDetected Intent:", result["intent"])
    print("Extracted Entities:", result["entities"])
    print("Relevant Services (semantic match):", result["services"])
    print("\nFinal Response:\n", result["response"])
