# ☁️ Cloud Cost Intelligence System  
## Hybrid Ontology-Driven Knowledge Graph with Semantic RAG

---

## 📌 Project Overview

This project implements a **Hybrid Retrieval-Augmented Generation (RAG) system** built on top of a **Neo4j ontology-driven cloud cost knowledge graph**.

The system supports:

- AWS and Azure cost ingestion
- Ontology-based cost modeling
- Semantic embedding retrieval
- Multi-hop graph reasoning
- Cross-cloud cost comparison
- Streamlit-based interactive UI
- Optional LLM-based explanation layer

This system moves beyond simple vector search by combining:

> **Graph reasoning + Semantic retrieval + Context-aware explanation**

---

## 🏗️ Architecture Overview

### 1️⃣ Data Layer
- AWS Cost & Usage Reports
- Azure Billing Export Data

### 2️⃣ Ontology Graph (Neo4j)

Core Entities:

- `Service`
- `Resource`
- `CostRecord`
- `Account`
- `Charge`
- `TimeFrame`
- `VendorSpecificAttributes`
- `Location`

Key Relationships:

- `INCURRED_BY`
- `USES_SERVICE`
- `HAS_CHARGE`
- `HAS_TIMEFRAME`
- `BELONGS_TO_BILLING_ACCOUNT`
- `HAS_VENDOR_ATTRS`
- `DEPLOYED_IN`

This ensures semantic richness and domain modeling.

---

## 🧠 Hybrid RAG Pipeline (v2)

### Step 1 — Intent Detection
Rule-based detection:
- Comparison
- Ranking
- Allocation
- Commitment
- Cost analysis

### Step 2 — Entity Extraction
Extract:
- Vendor (AWS / Azure)
- Service category (Storage / Compute)

### Step 3 — Semantic Retrieval
Uses:
to embed service nodes and perform similarity search.

### Step 4 — Graph Reasoning
Multi-hop traversal:

Concept-aware expansion:
- Storage → blob, disk, backup, file
- Compute → VM, instance, virtual

### Step 5 — Structured Response
- Vendor-level aggregation
- Service-level breakdown
- Cost difference calculation

### Step 6 — Optional LLM Layer
Context-aware explanation generation.
(Disabled automatically if API quota unavailable.)

---

## 💻 User Interface

Built using **Streamlit**.

Features:
- Natural language query input
- Intent detection display
- Extracted entity visualization
- Semantic match preview
- Structured reasoning output

Run locally:

```bash
streamlit run app.py

Concept-aware keyword expansion:

Storage → blob, disk, file, backup  
Compute → vm, instance, virtual  

Enables semantic category reasoning.

---

### Step 5 — Structured Analytical Response

Provides:

- Vendor-level totals
- Service-level breakdown
- Cost difference calculation
- Ranking output (if applicable)

Example Output:

Concept-aware keyword expansion:

Storage → blob, disk, file, backup  
Compute → vm, instance, virtual  

Enables semantic category reasoning.

---

### Step 5 — Structured Analytical Response

Provides:

- Vendor-level totals
- Service-level breakdown
- Cost difference calculation
- Ranking output (if applicable)

Example Output:

---

### Step 6 — Optional LLM Layer

LLM is integrated for:

- Analytical summary
- Vendor comparison explanation
- Business insight generation

If API quota is unavailable, system gracefully falls back to structured reasoning.

---

## 💻 User Interface (Streamlit)

Interactive UI built using Streamlit.

Displays:

- Detected intent
- Extracted entities
- Semantic matches
- Final structured reasoning
- Optional LLM analysis

Run locally:

```bash
streamlit run app.py

