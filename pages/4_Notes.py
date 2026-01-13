"""
Notes page - List, add, edit, delete notes with filtering by type and attached entity.
"""
import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
import database as db

st.set_page_config(page_title="Notes - Idea Vault", page_icon="📝", layout="wide")

# Initialize session state
if 'selected_note_id' not in st.session_state:
    st.session_state.selected_note_id = None
if 'note_edit_mode' not in st.session_state:
    st.session_state.note_edit_mode = False

st.title("📝 Notes")

# Tabs for List and Add/Edit
tab_list, tab_add_edit = st.tabs(["📋 List", "➕ Add/Edit"])

# =============================================================================
# LIST TAB
# =============================================================================
with tab_list:
    st.subheader("All Notes")

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_type = st.selectbox(
            "Filter by Type",
            ["All", "interview", "competitor", "pricing", "tech", "general"],
            key="note_filter_type"
        )
    with col_f2:
        # Filter by attached problem
        all_problems = db.get_all_problems()
        problem_filter_options = {"All": None}
        problem_filter_options.update({f"{p['id']}: {p['title'][:30]}": p['id'] for p in all_problems})
        filter_problem = st.selectbox("Filter by Problem", list(problem_filter_options.keys()), key="note_filter_problem")

    with col_f3:
        # Filter by attached idea
        all_ideas = db.get_all_ideas()
        idea_filter_options = {"All": None}
        idea_filter_options.update({f"{i['id']}: {i['title'][:30]}": i['id'] for i in all_ideas})
        filter_idea = st.selectbox("Filter by Idea", list(idea_filter_options.keys()), key="note_filter_idea")

    # Get and filter notes
    all_notes = db.get_all_notes()
    filtered_notes = all_notes.copy()

    if filter_type != "All":
        filtered_notes = [n for n in filtered_notes if n['note_type'] == filter_type]

    if filter_problem != "All":
        selected_problem_id = problem_filter_options[filter_problem]
        filtered_notes = [n for n in filtered_notes if n['problem_id'] == selected_problem_id]

    if filter_idea != "All":
        selected_idea_id = idea_filter_options[filter_idea]
        filtered_notes = [n for n in filtered_notes if n['idea_id'] == selected_idea_id]

    if filtered_notes:
        # Build display dataframe with entity names
        display_data = []
        for note in filtered_notes:
            problem_name = ""
            idea_name = ""
            if note['problem_id']:
                prob = db.get_problem_by_id(note['problem_id'])
                if prob:
                    problem_name = f"{prob['id']}: {prob['title'][:20]}"
            if note['idea_id']:
                idea_obj = db.get_idea_by_id(note['idea_id'])
                if idea_obj:
                    idea_name = f"{idea_obj['id']}: {idea_obj['title'][:20]}"

            display_data.append({
                'ID': note['id'],
                'Type': note['note_type'],
                'Content Preview': (note['content'][:50] + '...') if len(note['content']) > 50 else note['content'],
                'Problem': problem_name or '-',
                'Idea': idea_name or '-',
                'Created': note['created_at']
            })

        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Select note to view/edit
        st.markdown("---")
        note_options = {f"{n['id']}: {n['note_type']} - {n['content'][:30]}": n['id'] for n in filtered_notes}
        selected_option = st.selectbox(
            "Select a note to view details or edit:",
            [""] + list(note_options.keys()),
            key="note_select"
        )

        if selected_option:
            selected_id = note_options[selected_option]
            note = db.get_note_by_id(selected_id)

            if note:
                st.markdown("### Note Details")
                st.markdown(f"**Type:** {note['note_type']}")
                st.markdown(f"**Created:** {note['created_at']}")

                # Show attached entities
                if note['problem_id']:
                    prob = db.get_problem_by_id(note['problem_id'])
                    if prob:
                        st.markdown(f"**Attached to Problem:** {prob['id']}: {prob['title']}")

                if note['idea_id']:
                    idea_obj = db.get_idea_by_id(note['idea_id'])
                    if idea_obj:
                        st.markdown(f"**Attached to Idea:** {idea_obj['id']}: {idea_obj['title']}")

                st.markdown("**Content:**")
                st.text_area("", value=note['content'], disabled=True, key="note_content_view", height=200)

                if note['links']:
                    st.markdown(f"**Links:** {note['links']}")

                # Actions
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    if st.button("Edit this Note", key="note_edit_btn"):
                        st.session_state.selected_note_id = selected_id
                        st.session_state.note_edit_mode = True
                        st.rerun()

                with col_a2:
                    if st.button("Delete this Note", key="note_delete_btn", type="secondary"):
                        st.session_state.confirm_delete_note = selected_id

                # Confirm delete
                if 'confirm_delete_note' in st.session_state and st.session_state.confirm_delete_note == selected_id:
                    st.warning("Are you sure you want to delete this note?")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("Yes, Delete", key="note_confirm_del"):
                            if db.delete_note(selected_id):
                                st.success("Note deleted successfully!")
                                del st.session_state.confirm_delete_note
                                st.rerun()
                            else:
                                st.error("Failed to delete note.")
                    with col_c2:
                        if st.button("Cancel", key="note_cancel_del"):
                            del st.session_state.confirm_delete_note
                            st.rerun()
    else:
        st.info("No notes found matching your filters.")

# =============================================================================
# ADD/EDIT TAB
# =============================================================================
with tab_add_edit:
    # Check if we're editing an existing note
    editing = st.session_state.note_edit_mode and st.session_state.selected_note_id
    if editing:
        note = db.get_note_by_id(st.session_state.selected_note_id)
        st.subheader(f"Edit Note (ID: {note['id']})")
        if st.button("Cancel Edit", key="note_cancel_edit"):
            st.session_state.note_edit_mode = False
            st.session_state.selected_note_id = None
            st.rerun()
    else:
        note = None
        st.subheader("Add New Note")

    # Form fields
    with st.form("note_form"):
        type_options = ["interview", "competitor", "pricing", "tech", "general"]
        type_idx = type_options.index(note['note_type']) if note and note['note_type'] else 4
        note_type = st.selectbox("Note Type *", type_options, index=type_idx)

        content = st.text_area("Content *", value=note['content'] if note else "", height=200)
        links = st.text_input("Links (URLs, references, etc.)", value=note['links'] if note else "")

        st.markdown("**Attach to (optional):**")
        col1, col2 = st.columns(2)

        with col1:
            # Attach to problem
            all_problems = db.get_all_problems()
            problem_options = {"None": None}
            problem_options.update({f"{p['id']}: {p['title'][:40]}": p['id'] for p in all_problems})

            # Find current selection
            current_problem_selection = "None"
            if note and note['problem_id']:
                for k, v in problem_options.items():
                    if v == note['problem_id']:
                        current_problem_selection = k
                        break

            problem_keys = list(problem_options.keys())
            problem_idx = problem_keys.index(current_problem_selection) if current_problem_selection in problem_keys else 0
            selected_problem = st.selectbox("Attach to Problem", problem_keys, index=problem_idx)
            problem_id = problem_options[selected_problem]

        with col2:
            # Attach to idea
            all_ideas = db.get_all_ideas()
            idea_options = {"None": None}
            idea_options.update({f"{i['id']}: {i['title'][:40]}": i['id'] for i in all_ideas})

            # Find current selection
            current_idea_selection = "None"
            if note and note['idea_id']:
                for k, v in idea_options.items():
                    if v == note['idea_id']:
                        current_idea_selection = k
                        break

            idea_keys = list(idea_options.keys())
            idea_idx = idea_keys.index(current_idea_selection) if current_idea_selection in idea_keys else 0
            selected_idea = st.selectbox("Attach to Idea", idea_keys, index=idea_idx)
            idea_id = idea_options[selected_idea]

        submitted = st.form_submit_button("Save Note")

        if submitted:
            if not content.strip():
                st.error("Content is required!")
            else:
                if editing:
                    success = db.update_note(
                        st.session_state.selected_note_id,
                        note_type, content.strip(), links, problem_id, idea_id
                    )
                    if success:
                        st.success("Note updated successfully!")
                        st.session_state.note_edit_mode = False
                        st.session_state.selected_note_id = None
                        st.rerun()
                    else:
                        st.error("Failed to update note.")
                else:
                    note_id = db.create_note(
                        note_type, content.strip(), links, problem_id, idea_id
                    )
                    if note_id:
                        st.success(f"Note created successfully! (ID: {note_id})")
                        st.rerun()
                    else:
                        st.error("Failed to create note.")
