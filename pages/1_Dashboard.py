"""
Dashboard page - Overview of problems and ideas with status counts and recent items.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import database as db

st.set_page_config(page_title="Dashboard - Idea Vault", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.markdown("---")

# Status counts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Problems by Status")
    problem_counts = db.get_problems_count_by_status()
    if problem_counts:
        df_problems = pd.DataFrame([
            {"Status": status, "Count": count}
            for status, count in problem_counts.items()
        ])
        st.dataframe(df_problems, use_container_width=True, hide_index=True)

        # Show totals
        total_problems = sum(problem_counts.values())
        st.metric("Total Problems", total_problems)
    else:
        st.info("No problems recorded yet.")

with col2:
    st.subheader("Ideas by Status")
    idea_counts = db.get_ideas_count_by_status()
    if idea_counts:
        df_ideas = pd.DataFrame([
            {"Status": status, "Count": count}
            for status, count in idea_counts.items()
        ])
        st.dataframe(df_ideas, use_container_width=True, hide_index=True)

        # Show totals
        total_ideas = sum(idea_counts.values())
        st.metric("Total Ideas", total_ideas)
    else:
        st.info("No ideas recorded yet.")

st.markdown("---")

# Recent items
col3, col4 = st.columns(2)

with col3:
    st.subheader("Recently Added Problems")
    recent_problems = db.get_recent_problems(5)
    if recent_problems:
        df_recent_problems = pd.DataFrame(recent_problems)
        display_cols = ['id', 'title', 'status', 'severity', 'created_at']
        df_display = df_recent_problems[display_cols].copy()
        df_display.columns = ['ID', 'Title', 'Status', 'Severity', 'Created']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No problems recorded yet. Go to the Problems page to add one!")

with col4:
    st.subheader("Recently Added Ideas")
    recent_ideas = db.get_recent_ideas(5)
    if recent_ideas:
        df_recent_ideas = pd.DataFrame(recent_ideas)
        display_cols = ['id', 'title', 'status', 'score', 'created_at']
        df_display = df_recent_ideas[display_cols].copy()
        df_display.columns = ['ID', 'Title', 'Status', 'Score', 'Created']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No ideas recorded yet. Go to the Ideas page to add one!")

st.markdown("---")
st.caption("Use the sidebar to navigate to Problems, Ideas, or Notes pages.")
