"""
Idea Vault - Main entry point for the Streamlit multipage app.
A tool to track startup problems and ideas.
"""
import streamlit as st
import sys
from pathlib import Path

# Ensure database module is importable
sys.path.insert(0, str(Path(__file__).parent))
import database as db

# Initialize database tables on first run
@st.cache_resource
def initialize_database():
    """Initialize database tables (runs once per app lifecycle)."""
    db.init_db()
    return True

initialize_database()

st.set_page_config(
    page_title="Idea Vault",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation info
st.sidebar.title("🏦 Idea Vault")
st.sidebar.markdown("Track startup problems and ideas")
st.sidebar.markdown("---")
st.sidebar.markdown("**Navigation:**")
st.sidebar.markdown("Use the pages above to navigate.")

# Main page content
st.title("🏦 Welcome to Idea Vault")
st.markdown("---")

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

---
*Use the sidebar to navigate between pages.*
""")
