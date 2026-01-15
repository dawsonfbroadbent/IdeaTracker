"""
Idea Vault - Main entry point for the Streamlit multipage app.
A tool to track startup problems and ideas.

Data is stored locally in your browser using localStorage.
No server database required - works entirely offline.
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure database module is importable
sys.path.insert(0, str(Path(__file__).parent))
import database as db

# Initialize storage on first run
@st.cache_resource
def initialize_storage():
    """Initialize local storage structure (runs once per app lifecycle)."""
    db.init_db()
    return True

initialize_storage()

st.set_page_config(
    page_title="Idea Vault",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation info
st.sidebar.title("🏦 Idea Vault")
st.sidebar.markdown("Track startup problems and ideas")

# Local-only notice in sidebar
st.sidebar.markdown("---")
st.sidebar.info(
    "**Local Storage Only**\n\n"
    "Your data is saved in this browser only. "
    "It won't sync across devices or browsers."
)
st.sidebar.markdown("---")

st.sidebar.markdown("**Navigation:**")
st.sidebar.markdown("Use the pages above to navigate.")

# Main page content
st.title("🏦 Welcome to Idea Vault")
st.markdown("---")

# Prominent local-only notice
st.warning(
    "**Local-Only Storage:** Your data is stored in this browser's localStorage. "
    "It will not sync across devices, browsers, or private/incognito sessions. "
    "Use the Data Management section below to export backups."
)

st.markdown("""
## Your Startup Problem & Idea Tracker

**Idea Vault** helps you systematically track and manage:

- **Problems** - Pain points you've observed that could be solved
- **Ideas** - Potential solutions and startup concepts
- **Notes** - Research, interviews, and insights

### Getting Started

1. **📊 Dashboard** - View an overview of all your problems and ideas
2. **🔍 Problems** - Add and manage problems you've identified
3. **💡 Ideas** - Create and develop your solution ideas
4. **📝 Notes** - Capture research, interviews, and insights

### Quick Stats
""")

# Show quick stats
col1, col2, col3 = st.columns(3)

with col1:
    problem_counts = db.get_problems_count_by_status()
    total_problems = sum(problem_counts.values()) if problem_counts else 0
    st.metric("Total Problems", total_problems)

with col2:
    idea_counts = db.get_ideas_count_by_status()
    total_ideas = sum(idea_counts.values()) if idea_counts else 0
    st.metric("Total Ideas", total_ideas)

with col3:
    all_notes = db.get_all_notes()
    st.metric("Total Notes", len(all_notes))

st.markdown("---")

st.markdown("""
### Tips

- **Link ideas to problems** to track which solutions address which pain points
- **Use tags** to organize and filter your entries
- **Add notes** for research, competitor analysis, interviews, and more
- **Update statuses** as you progress through validation stages
- **Export your data regularly** to keep backups
""")

st.markdown("---")

# Data Management Section
st.subheader("Data Management")
st.markdown("Export and import your data for backups or transferring between devices.")

col_export, col_import = st.columns(2)

with col_export:
    st.markdown("**Export Data**")
    if st.button("Generate Export"):
        import json
        data = db.export_all_data()
        json_str = json.dumps(data, indent=2, default=str)
        st.download_button(
            label="Download JSON Backup",
            data=json_str,
            file_name="idea_vault_backup.json",
            mime="application/json"
        )
        st.success("Export ready! Click the download button above.")

with col_import:
    st.markdown("**Import Data**")
    uploaded_file = st.file_uploader("Upload JSON backup", type=['json'])
    if uploaded_file is not None:
        import json
        try:
            data = json.load(uploaded_file)
            if st.button("Import Data (Replaces Current)", type="secondary"):
                if db.import_all_data(data):
                    st.success("Data imported successfully! Refresh the page to see changes.")
                    st.rerun()
                else:
                    st.error("Failed to import data. Check the file format.")
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")

st.markdown("---")

# Clear data option (with confirmation)
with st.expander("Danger Zone - Clear All Data"):
    st.warning("This will permanently delete all your problems, ideas, notes, and links.")
    confirm_text = st.text_input("Type 'DELETE' to confirm:")
    if st.button("Clear All Data", type="secondary", disabled=(confirm_text != "DELETE")):
        db.clear_all_data()
        st.success("All data cleared. Refresh the page.")
        st.rerun()

st.markdown("---")
st.caption("*Use the sidebar to navigate between pages.*")
