import streamlit as st
from rag_v2 import run_rag

st.set_page_config(page_title="Cloud Cost Knowledge Graph Assistant", layout="centered")

st.title("☁️ Cloud Cost Intelligence Assistant (Hybrid RAG v2)")

st.markdown("""
Ask advanced natural language questions about:

- AWS vs Azure comparison
- Storage / Compute cost
- Ranking of services
- Commitment / Allocation analysis
""")

query = st.text_input("Ask your cloud cost question:")

if st.button("Analyze"):

    if not query.strip():
        st.warning("Please enter a question.")
    else:
        result = run_rag(query)

        st.markdown("### 🔍 Detected Intent")
        st.write(result["intent"])

        st.markdown("### 🏷 Extracted Entities")
        st.json(result["entities"])

        st.markdown("### 🧠 Semantic Service Matches")
        st.write(result["services"])

        st.markdown("### 📊 Final Analysis")
        st.text(result["response"])