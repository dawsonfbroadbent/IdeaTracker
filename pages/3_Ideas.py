"""
Ideas page - List, add, edit, delete ideas with filtering, problem linking, and detail view.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import database as db

st.set_page_config(page_title="Ideas - Idea Vault", page_icon="💡", layout="wide")

# Initialize session state
if 'selected_idea_id' not in st.session_state:
    st.session_state.selected_idea_id = None
if 'idea_edit_mode' not in st.session_state:
    st.session_state.idea_edit_mode = False

st.title("💡 Ideas")

# Tabs for List and Add/Edit
tab_list, tab_add_edit = st.tabs(["📋 List", "➕ Add/Edit"])

# =============================================================================
# LIST TAB
# =============================================================================
with tab_list:
    st.subheader("All Ideas")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "new", "researching", "validating", "building", "parked"],
            key="idea_filter_status"
        )
    with col_f2:
        filter_tags = st.text_input("Filter by Tags (comma-separated)", key="idea_filter_tags")
    with col_f3:
        keyword_search = st.text_input("Keyword Search", key="idea_keyword_search")

    # Get and filter ideas
    all_ideas = db.get_all_ideas()
    filtered_ideas = all_ideas.copy()

    if filter_status != "All":
        filtered_ideas = [i for i in filtered_ideas if i['status'] == filter_status]

    if filter_tags:
        tag_filters = [t.strip().lower() for t in filter_tags.split(',') if t.strip()]
        filtered_ideas = [
            i for i in filtered_ideas
            if i['tags'] and any(tag in i['tags'].lower() for tag in tag_filters)
        ]

    if keyword_search:
        keyword = keyword_search.lower()
        filtered_ideas = [
            i for i in filtered_ideas
            if keyword in (i['title'] or '').lower() or keyword in (i['pitch'] or '').lower()
        ]

    if filtered_ideas:
        df = pd.DataFrame(filtered_ideas)
        display_cols = ['id', 'title', 'pitch', 'status', 'score', 'tags', 'created_at']
        df_display = df[display_cols].copy()
        df_display.columns = ['ID', 'Title', 'Pitch', 'Status', 'Score', 'Tags', 'Created']
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Select idea to view/edit
        st.markdown("---")
        idea_options = {f"{i['id']}: {i['title'][:50]}": i['id'] for i in filtered_ideas}
        selected_option = st.selectbox(
            "Select an idea to view details or edit:",
            [""] + list(idea_options.keys()),
            key="idea_select"
        )

        if selected_option:
            selected_id = idea_options[selected_option]
            idea = db.get_idea_by_id(selected_id)

            if idea:
                st.markdown("### Idea Details")
                col_d1, col_d2 = st.columns(2)

                with col_d1:
                    st.markdown(f"**Title:** {idea['title']}")
                    st.markdown(f"**Pitch:** {idea['pitch'] or 'N/A'}")
                    st.markdown(f"**Target User:** {idea['target_user'] or 'N/A'}")
                    st.markdown(f"**Status:** {idea['status']}")
                    st.markdown(f"**Score:** {idea['score'] if idea['score'] is not None else 'N/A'}")
                    st.markdown(f"**Tags:** {idea['tags'] or 'None'}")

                with col_d2:
                    st.markdown(f"**Created:** {idea['created_at']}")
                    st.markdown(f"**Updated:** {idea['updated_at']}")

                st.markdown("**Value Proposition:**")
                st.text_area("", value=idea['value_prop'] or '', disabled=True, key="idea_vp_view", height=80)

                st.markdown("**Differentiation:**")
                st.text_area("", value=idea['differentiation'] or '', disabled=True, key="idea_diff_view", height=80)

                st.markdown("**Assumptions:**")
                st.text_area("", value=idea['assumptions'] or '', disabled=True, key="idea_assump_view", height=80)

                st.markdown("**Risks:**")
                st.text_area("", value=idea['risks'] or '', disabled=True, key="idea_risks_view", height=80)

                # Quick Status Update
                st.markdown("### Quick Status Update")
                status_options = ["new", "researching", "validating", "building", "parked"]
                current_idx = status_options.index(idea['status']) if idea['status'] in status_options else 0
                new_status = st.selectbox("Update Status", status_options, index=current_idx, key="idea_quick_status")
                if new_status != idea['status']:
                    if st.button("Save Status", key="idea_save_status"):
                        db.update_idea(
                            selected_id, idea['title'], idea['pitch'], idea['target_user'],
                            idea['value_prop'], idea['differentiation'], idea['assumptions'],
                            idea['risks'], new_status, idea['score'], idea['tags']
                        )
                        st.success("Status updated!")
                        st.rerun()

                # Linked Problems
                st.markdown("### Linked Problems")
                linked_problems = db.get_problems_for_idea(selected_id)
                if linked_problems:
                    df_probs = pd.DataFrame(linked_problems)
                    st.dataframe(df_probs[['id', 'title', 'status', 'severity']], use_container_width=True, hide_index=True)
                else:
                    st.info("No problems linked to this idea yet.")

                # Notes for this idea
                st.markdown("### Notes")
                notes = db.get_notes_for_idea(selected_id)
                if notes:
                    for note in notes:
                        with st.expander(f"{note['note_type'].upper()} - {note['created_at'][:10]}"):
                            st.write(note['content'])
                            if note['links']:
                                st.markdown(f"**Links:** {note['links']}")
                else:
                    st.info("No notes attached to this idea yet.")

                # Actions
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("Edit this Idea", key="idea_edit_btn"):
                        st.session_state.selected_idea_id = selected_id
                        st.session_state.idea_edit_mode = True
                        st.rerun()

                with col_a2:
                    if st.button("Delete this Idea", key="idea_delete_btn", type="secondary"):
                        st.session_state.confirm_delete_idea = selected_id

                # Confirm delete
                if 'confirm_delete_idea' in st.session_state and st.session_state.confirm_delete_idea == selected_id:
                    st.warning("Are you sure you want to delete this idea?")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("Yes, Delete", key="idea_confirm_del"):
                            if db.delete_idea(selected_id):
                                st.success("Idea deleted successfully!")
                                del st.session_state.confirm_delete_idea
                                st.rerun()
                            else:
                                st.error("Failed to delete idea.")
                    with col_c2:
                        if st.button("Cancel", key="idea_cancel_del"):
                            del st.session_state.confirm_delete_idea
                            st.rerun()
    else:
        st.info("No ideas found matching your filters.")

# =============================================================================
# ADD/EDIT TAB
# =============================================================================
with tab_add_edit:
    # Check if we're editing an existing idea
    editing = st.session_state.idea_edit_mode and st.session_state.selected_idea_id
    if editing:
        idea = db.get_idea_by_id(st.session_state.selected_idea_id)
        st.subheader(f"Edit Idea: {idea['title']}")
        if st.button("Cancel Edit", key="idea_cancel_edit"):
            st.session_state.idea_edit_mode = False
            st.session_state.selected_idea_id = None
            st.rerun()
    else:
        idea = None
        st.subheader("Add New Idea")

    # Form fields
    with st.form("idea_form"):
        title = st.text_input("Title *", value=idea['title'] if idea else "", max_chars=200)
        pitch = st.text_input("Pitch (1 sentence)", value=idea['pitch'] if idea else "", max_chars=300)
        target_user = st.text_input("Target User", value=idea['target_user'] if idea else "")
        value_prop = st.text_area("Value Proposition", value=idea['value_prop'] if idea else "", height=100)
        differentiation = st.text_area("Differentiation", value=idea['differentiation'] if idea else "", height=100)
        assumptions = st.text_area("Assumptions", value=idea['assumptions'] if idea else "", height=100)
        risks = st.text_area("Risks", value=idea['risks'] if idea else "", height=100)

        col1, col2 = st.columns(2)
        with col1:
            status_options = ["new", "researching", "validating", "building", "parked"]
            status_idx = status_options.index(idea['status']) if idea and idea['status'] else 0
            status = st.selectbox("Status", status_options, index=status_idx)
        with col2:
            score_val = idea['score'] if idea and idea['score'] is not None else 50
            score = st.slider("Score (0-100, optional)", 0, 100, value=score_val)
            use_score = st.checkbox("Set score", value=(idea['score'] is not None) if idea else False)

        tags = st.text_input("Tags (comma-separated)", value=idea['tags'] if idea else "")

        # Link to problems (multiselect)
        st.markdown("**Link to Problems:**")
        all_problems = db.get_all_problems()
        problem_options = {f"{p['id']}: {p['title'][:40]}": p['id'] for p in all_problems}

        # Get currently linked problem IDs
        current_linked_ids = []
        if editing:
            current_linked_ids = db.get_linked_problem_ids_for_idea(st.session_state.selected_idea_id)

        # Pre-select currently linked problems
        default_selection = [k for k, v in problem_options.items() if v in current_linked_ids]
        selected_problems = st.multiselect(
            "Select problems to link",
            options=list(problem_options.keys()),
            default=default_selection
        )

        submitted = st.form_submit_button("Save Idea")

        if submitted:
            if not title.strip():
                st.error("Title is required!")
            else:
                final_score = score if use_score else None
                selected_problem_ids = [problem_options[p] for p in selected_problems]

                if editing:
                    success = db.update_idea(
                        st.session_state.selected_idea_id,
                        title.strip(), pitch, target_user, value_prop,
                        differentiation, assumptions, risks, status, final_score, tags
                    )
                    if success:
                        # Update problem links
                        db.set_problem_links_for_idea(st.session_state.selected_idea_id, selected_problem_ids)
                        st.success("Idea updated successfully!")
                        st.session_state.idea_edit_mode = False
                        st.session_state.selected_idea_id = None
                        st.rerun()
                    else:
                        st.error("Failed to update idea.")
                else:
                    idea_id = db.create_idea(
                        title.strip(), pitch, target_user, value_prop,
                        differentiation, assumptions, risks, status, final_score, tags
                    )
                    if idea_id:
                        # Set problem links
                        db.set_problem_links_for_idea(idea_id, selected_problem_ids)
                        st.success(f"Idea created successfully! (ID: {idea_id})")
                        st.rerun()
                    else:
                        st.error("Failed to create idea.")
