"""
Problems page - List, add, edit, delete problems with filtering and detail view.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import database as db

st.set_page_config(page_title="Problems - Idea Vault", page_icon="🔍", layout="wide")

# Initialize session state
if 'selected_problem_id' not in st.session_state:
    st.session_state.selected_problem_id = None
if 'problem_edit_mode' not in st.session_state:
    st.session_state.problem_edit_mode = False

st.title("🔍 Problems")

# Tabs for List and Add/Edit
tab_list, tab_add_edit = st.tabs(["📋 List", "➕ Add/Edit"])

# =============================================================================
# LIST TAB
# =============================================================================
with tab_list:
    st.subheader("All Problems")

    # Filters
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filter_status = st.selectbox("Filter by Status", ["All", "open", "solved", "ignored"], key="prob_filter_status")
    with col_f2:
        filter_severity = st.selectbox("Filter by Severity", ["All", 1, 2, 3, 4, 5], key="prob_filter_severity")
    with col_f3:
        filter_tags = st.text_input("Filter by Tags (comma-separated)", key="prob_filter_tags")
    with col_f4:
        keyword_search = st.text_input("Keyword Search", key="prob_keyword_search")

    # Get and filter problems
    all_problems = db.get_all_problems()
    filtered_problems = all_problems.copy()

    if filter_status != "All":
        filtered_problems = [p for p in filtered_problems if p['status'] == filter_status]

    if filter_severity != "All":
        filtered_problems = [p for p in filtered_problems if p['severity'] == filter_severity]

    if filter_tags:
        tag_filters = [t.strip().lower() for t in filter_tags.split(',') if t.strip()]
        filtered_problems = [
            p for p in filtered_problems
            if p['tags'] and any(tag in p['tags'].lower() for tag in tag_filters)
        ]

    if keyword_search:
        keyword = keyword_search.lower()
        filtered_problems = [
            p for p in filtered_problems
            if keyword in (p['title'] or '').lower() or keyword in (p['description'] or '').lower()
        ]

    if filtered_problems:
        df = pd.DataFrame(filtered_problems)
        display_cols = ['id', 'title', 'status', 'severity', 'frequency', 'tags', 'created_at']
        df_display = df[display_cols].copy()
        df_display.columns = ['ID', 'Title', 'Status', 'Severity', 'Frequency', 'Tags', 'Created']
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Select problem to view/edit
        st.markdown("---")
        problem_options = {f"{p['id']}: {p['title'][:50]}": p['id'] for p in filtered_problems}
        selected_option = st.selectbox(
            "Select a problem to view details or edit:",
            [""] + list(problem_options.keys()),
            key="prob_select"
        )

        if selected_option:
            selected_id = problem_options[selected_option]
            problem = db.get_problem_by_id(selected_id)

            if problem:
                st.markdown("### Problem Details")
                col_d1, col_d2 = st.columns(2)

                with col_d1:
                    st.markdown(f"**Title:** {problem['title']}")
                    st.markdown(f"**Status:** {problem['status']}")
                    st.markdown(f"**Severity:** {problem['severity']}/5")
                    st.markdown(f"**Frequency:** {problem['frequency']}")
                    st.markdown(f"**Tags:** {problem['tags'] or 'None'}")

                with col_d2:
                    st.markdown(f"**Created:** {problem['created_at']}")
                    st.markdown(f"**Updated:** {problem['updated_at']}")

                st.markdown("**Description:**")
                st.text_area("", value=problem['description'] or '', disabled=True, key="prob_desc_view", height=100)

                st.markdown("**Observed Context:**")
                st.text_area("", value=problem['observed_context'] or '', disabled=True, key="prob_ctx_view", height=100)

                # Linked Ideas
                st.markdown("### Linked Ideas")
                linked_ideas = db.get_ideas_for_problem(selected_id)
                if linked_ideas:
                    df_ideas = pd.DataFrame(linked_ideas)
                    st.dataframe(df_ideas[['id', 'title', 'status', 'score']], use_container_width=True, hide_index=True)
                else:
                    st.info("No ideas linked to this problem yet.")

                # Notes for this problem
                st.markdown("### Notes")
                notes = db.get_notes_for_problem(selected_id)
                if notes:
                    for note in notes:
                        with st.expander(f"{note['note_type'].upper()} - {note['created_at'][:10]}"):
                            st.write(note['content'])
                            if note['links']:
                                st.markdown(f"**Links:** {note['links']}")
                else:
                    st.info("No notes attached to this problem yet.")

                # Actions
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("Edit this Problem", key="prob_edit_btn"):
                        st.session_state.selected_problem_id = selected_id
                        st.session_state.problem_edit_mode = True
                        st.rerun()

                with col_a2:
                    if st.button("Delete this Problem", key="prob_delete_btn", type="secondary"):
                        st.session_state.confirm_delete_problem = selected_id

                # Confirm delete
                if 'confirm_delete_problem' in st.session_state and st.session_state.confirm_delete_problem == selected_id:
                    st.warning("Are you sure you want to delete this problem?")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("Yes, Delete", key="prob_confirm_del"):
                            if db.delete_problem(selected_id):
                                st.success("Problem deleted successfully!")
                                del st.session_state.confirm_delete_problem
                                st.rerun()
                            else:
                                st.error("Failed to delete problem.")
                    with col_c2:
                        if st.button("Cancel", key="prob_cancel_del"):
                            del st.session_state.confirm_delete_problem
                            st.rerun()
    else:
        st.info("No problems found matching your filters.")

# =============================================================================
# ADD/EDIT TAB
# =============================================================================
with tab_add_edit:
    # Check if we're editing an existing problem
    editing = st.session_state.problem_edit_mode and st.session_state.selected_problem_id
    if editing:
        problem = db.get_problem_by_id(st.session_state.selected_problem_id)
        st.subheader(f"Edit Problem: {problem['title']}")
        if st.button("Cancel Edit", key="prob_cancel_edit"):
            st.session_state.problem_edit_mode = False
            st.session_state.selected_problem_id = None
            st.rerun()
    else:
        problem = None
        st.subheader("Add New Problem")

    # Form fields
    with st.form("problem_form"):
        title = st.text_input("Title *", value=problem['title'] if problem else "", max_chars=200)
        description = st.text_area("Description", value=problem['description'] if problem else "", height=150)
        observed_context = st.text_area("Observed Context", value=problem['observed_context'] if problem else "", height=100)

        col1, col2, col3 = st.columns(3)
        with col1:
            severity = st.slider("Severity", 1, 5, value=problem['severity'] if problem else 3)
        with col2:
            frequency_options = ["rare", "weekly", "daily"]
            frequency_idx = frequency_options.index(problem['frequency']) if problem and problem['frequency'] else 1
            frequency = st.selectbox("Frequency", frequency_options, index=frequency_idx)
        with col3:
            status_options = ["open", "solved", "ignored"]
            status_idx = status_options.index(problem['status']) if problem and problem['status'] else 0
            status = st.selectbox("Status", status_options, index=status_idx)

        tags = st.text_input("Tags (comma-separated)", value=problem['tags'] if problem else "")

        submitted = st.form_submit_button("Save Problem")

        if submitted:
            if not title.strip():
                st.error("Title is required!")
            else:
                if editing:
                    success = db.update_problem(
                        st.session_state.selected_problem_id,
                        title.strip(), description, observed_context,
                        severity, frequency, status, tags
                    )
                    if success:
                        st.success("Problem updated successfully!")
                        st.session_state.problem_edit_mode = False
                        st.session_state.selected_problem_id = None
                        st.rerun()
                    else:
                        st.error("Failed to update problem.")
                else:
                    problem_id = db.create_problem(
                        title.strip(), description, observed_context,
                        severity, frequency, status, tags
                    )
                    if problem_id:
                        st.success(f"Problem created successfully! (ID: {problem_id})")
                        st.rerun()
                    else:
                        st.error("Failed to create problem.")
