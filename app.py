import streamlit as st
from hybrid_query import find_best_service, get_cost_data

st.set_page_config(page_title="Cloud Cost Knowledge Graph Assistant", layout="centered")

st.title("☁️ Cloud Cost Knowledge Graph Assistant")

st.markdown("Ask natural language questions about your AWS/Azure cloud spend.")

query = st.text_input("Ask about cloud cost:")

if st.button("Analyze"):

    if not query.strip():
        st.warning("Please enter a question.")
    else:
        best_service = find_best_service(query)
        data = get_cost_data(best_service)

        if data:
            total_cost = data['total_cost']
            records = data['records']

            st.success(f"Most Relevant Service Identified: {best_service}")

            st.markdown("### 💰 Cost Analysis Result")
            st.write(
                f"The total cost for **{best_service}** is "
                f"**${total_cost}**, calculated from **{records} billing records**."
            )

        else:
            st.error("No data found for this query.")
