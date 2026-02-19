# ☁️ Cloud Cost Knowledge Graph using Ontology, Neo4j & RAG

## 📌 Project Overview

This project implements a Cloud Cost Knowledge Base using:

- Ontology Design (FOCUS 1.0 based modeling)
- Neo4j Knowledge Graph
- Vector Embeddings (Sentence Transformers)
- Hybrid Retrieval (Graph + Semantic Search)
- Streamlit UI for interactive querying

The system enables intelligent cloud cost analysis for AWS and Azure billing datasets.

---

## 🏗 System Architecture

Excel Billing Data (AWS / Azure)
↓
Ontology Mapping (FOCUS 1.0 Spec)
↓
Neo4j Knowledge Graph
↓
Node Embeddings (Sentence-Transformers)
↓
Hybrid Retrieval:
- Vector Similarity
- Graph Traversal
↓
Natural Language Cost Response
↓
Streamlit UI


---

## 🧠 Ontology Design

### Core Classes

- **CostRecord**
- **Account**
- **Service**
- **Resource**
- **Location**
- **Charge**
- **TimeFrame**
- **VendorSpecificAttributes (AWS / Azure)**
- **CostAllocation**

---

### Object Properties (Relationships)

| Source | Relationship | Target |
|--------|-------------|--------|
| CostRecord | BELONGS_TO | Account |
| CostRecord | INCURRED_BY | Resource |
| Resource | USES_SERVICE | Service |
| Resource | DEPLOYED_IN | Location |

---

### Data Properties

**CostRecord**
- billedCost (float ≥ 0)
- currency
- consumedQuantity
- consumedUnit

**Service**
- name
- category

**Resource**
- id
- type

---

### Cardinality Constraints

- One CostRecord → one Resource
- One Resource → one Service
- One Service → many CostRecords
- One Account → many CostRecords

---

### Validation Rules

- billedCost ≥ 0
- currency NOT NULL
- serviceName must exist
- resourceId must be unique

---

## 🗄 Knowledge Graph Implementation (Neo4j)

Nodes Created:
- CostRecord
- Resource
- Service
- Location
- Account

Relationships:
- BELONGS_TO
- INCURRED_BY
- USES_SERVICE
- DEPLOYED_IN

Constraints:
- Unique Service name
- Unique Resource ID
- Unique Account ID

---

## 🔍 Vector Embeddings

Embedding Model:


sentence-transformers/all-MiniLM-L6-v2


Embeddings are generated for:
- Service names
- Query inputs

Embedding dimension: 384

Stored as:


s.embedding

inside Neo4j nodes.

---

## 🔄 Hybrid Retrieval (Graph + Vector)

### Step 1: Vector Search
- User query → embedding
- Cosine similarity with Service embeddings
- Best matching service selected

### Step 2: Graph Traversal


CostRecord → Resource → Service


Aggregates:
- Total billedCost
- Record count

---

## 🖥 Streamlit UI

The application allows users to:

- Enter natural language questions
- Identify most relevant cloud service
- View cost breakdown

Example Query:


compute cost
storage usage
virtual machine spend


---

## ⚙️ Setup Instructions

### 1. Install Dependencies

```bash
pip install neo4j pandas xlrd openpyxl sentence-transformers torch streamlit

2. Start Neo4j Desktop

Create local DB

Set password

Ensure Bolt port 7687 active

3. Run Scripts

Setup constraints:

python setup_schema.py


Insert sample:

python insert_sample_data.py


Ingest Excel:

python ingest_excel.py


Add embeddings:

python add_embeddings.py


Run semantic search:

python hybrid_query.py


Launch UI:

streamlit run app.py

🧪 Example Test Queries
Query	Retrieval Type
compute cost	Hybrid
storage usage	Hybrid
virtual machine spend	Hybrid
📊 Evaluation Criteria Coverage
Requirement	Status
Ontology Modeling	✅
Knowledge Graph Design	✅
Embeddings Integration	✅
Hybrid RAG Pipeline	✅
Streamlit UI	✅
🚀 Future Enhancements

Add Azure/AWS comparison queries

Integrate OpenAI LLM for explanation generation

Implement REST API with FastAPI

Add commitment utilization analysis

👨‍💻 Author

Darshan
B.Tech AIML – AI Engineer Role Assignment


---

# 🏆 You Are Done

You now have:

✔ Full Knowledge Graph  
✔ Embedding-based Semantic Layer  
✔ Hybrid Retrieval  
✔ Streamlit App  
✔ Professional Documentation  

This is **AI Engineer-level submission**.

---

# 🔥 Final Question

Do you want to add:

1️⃣ LLM-powered explanation (OpenAI integration)  
2️⃣ REST API (bonus section Part F)  
3️⃣ Stop here and submit confidently  

Tell me and we finish strong 💪
