import streamlit as st
import requests
import pandas as pd
import time
import os

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI DB Query Optimizer", layout="wide", page_icon="🔍")

st.title("🤖 AI-Driven Self-Healing DB Optimizer")
st.markdown("Monitor database queries, analyze execution plans, and apply AI-recommended indexes to self-heal performance bottlenecks.")

# Sidebar Controls
st.sidebar.header("Controls")
if st.sidebar.button("Refresh Slow Queries"):
    pass # Will refresh naturally

tab1, tab2 = st.tabs(["🚀 Query Optimization", "🧹 Index Maintenance"])

with tab1:
    st.header("📊 Top Slow Queries")
    
    # Fetch slow queries from API
    try:
        response = requests.get(f"{API_URL}/api/slow_queries")
        if response.status_code == 200:
            queries = response.json()
            if queries:
                df = pd.DataFrame(queries)
                df.columns = ["Query", "Avg Execution Time (ms)", "Execution Count"]
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                st.header("🔍 Analyze & Auto-Heal")
                
                # Using forms to prevent immediate reruns or maintain state
                selected_query = st.selectbox("Select a query to analyze:", df["Query"].tolist())
                
                if st.button("Analyze Query with AI"):
                    with st.spinner("Analyzing EXPLAIN QUERY PLAN..."):
                        analyze_resp = requests.post(f"{API_URL}/api/analyze", params={"query": selected_query})
                        if analyze_resp.status_code == 200:
                            st.session_state['analysis'] = analyze_resp.json()
                        else:
                            st.error("Failed to analyze query.")
                            
                if 'analysis' in st.session_state:
                    analysis = st.session_state['analysis']
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Query Plan")
                        for line in analysis["plan"]:
                            st.code(line, language="sql")
                        
                        st.warning(f"**Bottleneck Detected:** {analysis['bottleneck']}")
                        
                    with col2:
                        st.subheader("AI Recommendation")
                        rec = analysis.get("recommendation")
                        if rec:
                            st.success(f"**Action:** {rec['type']}")
                            st.write(rec['description'])
                            
                            if rec['sql']:
                                st.code(rec['sql'], language="sql")
                                
                                # Auto-Heal Button
                                if st.button("🚀 Apply Auto-Heal (Execute Fix)"):
                                    heal_resp = requests.post(f"{API_URL}/api/heal", json={"sql_command": rec['sql']})
                                    if heal_resp.status_code == 200:
                                        st.balloons()
                                        st.success("Optimization applied successfully! Run queries again to see the performance improvement.")
                                        # Clear state so we don't keep showing the analysis for an old query
                                        del st.session_state['analysis']
                                    else:
                                        st.error(f"Failed to apply fix: {heal_resp.text}")
                        else:
                            st.info("No recommendations found. The query might already be optimized or is too complex.")
                            
            else:
                st.info("No slow queries logged yet. Run your workload first!")
                
    except requests.exceptions.ConnectionError:
        st.error(f"⚠️ Could not connect to the Backend API at {API_URL}. Ensure the FastAPI server is running.")

with tab2:
    st.header("🧹 Unused & Redundant Indexes")
    st.markdown("The AI monitors index usage and suggests removing ones that are never used to speed up database writes (INSERT/UPDATE/DELETE).")
    try:
        idx_resp = requests.get(f"{API_URL}/api/index_maintenance")
        if idx_resp.status_code == 200:
            suggestions = idx_resp.json()
            if suggestions:
                for idx, sugg in enumerate(suggestions):
                    st.warning(f"**Redundant Index Detected:** `{sugg['index_name']}` on table `{sugg['table']}`")
                    st.write(f"**Reason:** {sugg['reason']}")
                    st.code(sugg['sql'], language="sql")
                    if st.button(f"🗑️ Remove Index ({sugg['index_name']})", key=f"drop_{idx}"):
                        heal_resp = requests.post(f"{API_URL}/api/heal", json={"sql_command": sugg['sql']})
                        if heal_resp.status_code == 200:
                            st.success(f"Successfully dropped {sugg['index_name']}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to remove index.")
                    st.markdown("---")
            else:
                st.success("No redundant indexes found! Your database is clean.")
    except Exception as e:
        st.error("Could not fetch index maintenance data.")

st.sidebar.markdown("---")
st.sidebar.info("This is an Academic Level DB Optimizer testing simulated workload and execution plans for Self-Healing.")
