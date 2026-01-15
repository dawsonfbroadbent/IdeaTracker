"""
Database module for Idea Vault - Local browser storage wrapper.

This module provides a compatible API with the original PostgreSQL implementation,
but uses browser localStorage for persistence via streamlit-local-storage.

Data is stored locally in your browser and is NOT synced across devices.
"""

# Re-export all functions from storage module for backward compatibility
from storage import (
    # Initialization
    init_db,

    # Problems CRUD
    create_problem,
    get_all_problems,
    get_problem_by_id,
    update_problem,
    delete_problem,
    get_problems_count_by_status,
    get_recent_problems,

    # Ideas CRUD
    create_idea,
    get_all_ideas,
    get_idea_by_id,
    update_idea,
    delete_idea,
    get_ideas_count_by_status,
    get_recent_ideas,

    # Problem-Idea Links
    link_problem_to_idea,
    unlink_problem_from_idea,
    get_ideas_for_problem,
    get_problems_for_idea,
    get_linked_problem_ids_for_idea,
    set_problem_links_for_idea,

    # Notes CRUD
    create_note,
    get_all_notes,
    get_note_by_id,
    update_note,
    delete_note,
    get_notes_for_problem,
    get_notes_for_idea,

    # Data management
    export_all_data,
    import_all_data,
    clear_all_data,
)
