"""
Local Storage module for Idea Vault - Browser-based persistence using streamlit-local-storage.
Data is stored in the browser's localStorage, private to each device/browser.
"""
import streamlit as st
from streamlit_local_storage import LocalStorage
from datetime import datetime
from typing import Optional
import json

# Initialize local storage with a unique key prefix
_local_storage = None

def _get_storage() -> LocalStorage:
    """Get or create the LocalStorage instance."""
    global _local_storage
    if _local_storage is None:
        _local_storage = LocalStorage()
    return _local_storage


def _get_data(key: str, default=None):
    """Get data from local storage."""
    storage = _get_storage()
    try:
        value = storage.getItem(key)
        if value is None:
            return default
        return json.loads(value) if isinstance(value, str) else value
    except Exception:
        return default


def _set_data(key: str, value):
    """Set data in local storage."""
    storage = _get_storage()
    try:
        storage.setItem(key, json.dumps(value))
    except Exception as e:
        st.error(f"Failed to save data: {e}")


def _get_next_id(key: str) -> int:
    """Get the next available ID for a collection."""
    counter_key = f"ideavault_counter_{key}"
    current = _get_data(counter_key, 0)
    next_id = current + 1
    _set_data(counter_key, next_id)
    return next_id


# =============================================================================
# INITIALIZATION
# =============================================================================

def init_db():
    """Initialize storage structure if needed (no-op for localStorage, but ensures keys exist)."""
    # Initialize empty arrays if they don't exist
    if _get_data("ideavault_problems") is None:
        _set_data("ideavault_problems", [])
    if _get_data("ideavault_ideas") is None:
        _set_data("ideavault_ideas", [])
    if _get_data("ideavault_notes") is None:
        _set_data("ideavault_notes", [])
    if _get_data("ideavault_problem_idea_links") is None:
        _set_data("ideavault_problem_idea_links", [])


# =============================================================================
# PROBLEMS CRUD
# =============================================================================

def create_problem(title: str, description: str = "", observed_context: str = "",
                   severity: int = 3, frequency: str = "weekly", status: str = "open",
                   tags: str = "") -> int:
    """Create a new problem and return its ID."""
    problems = _get_data("ideavault_problems", [])
    now = datetime.now().isoformat()
    problem_id = _get_next_id("problems")

    problem = {
        "id": problem_id,
        "title": title,
        "description": description,
        "observed_context": observed_context,
        "severity": severity,
        "frequency": frequency,
        "status": status,
        "tags": tags,
        "created_at": now,
        "updated_at": now
    }

    problems.append(problem)
    _set_data("ideavault_problems", problems)
    return problem_id


def get_all_problems() -> list[dict]:
    """Get all problems as a list of dicts."""
    problems = _get_data("ideavault_problems", [])
    # Sort by created_at descending
    return sorted(problems, key=lambda x: x.get('created_at', ''), reverse=True)


def get_problem_by_id(problem_id: int) -> Optional[dict]:
    """Get a single problem by ID."""
    problems = _get_data("ideavault_problems", [])
    for p in problems:
        if p['id'] == problem_id:
            return p
    return None


def update_problem(problem_id: int, title: str, description: str, observed_context: str,
                   severity: int, frequency: str, status: str, tags: str) -> bool:
    """Update an existing problem."""
    problems = _get_data("ideavault_problems", [])
    now = datetime.now().isoformat()

    for i, p in enumerate(problems):
        if p['id'] == problem_id:
            problems[i].update({
                "title": title,
                "description": description,
                "observed_context": observed_context,
                "severity": severity,
                "frequency": frequency,
                "status": status,
                "tags": tags,
                "updated_at": now
            })
            _set_data("ideavault_problems", problems)
            return True
    return False


def delete_problem(problem_id: int) -> bool:
    """Delete a problem by ID (also removes related links and nullifies note references)."""
    problems = _get_data("ideavault_problems", [])
    original_len = len(problems)
    problems = [p for p in problems if p['id'] != problem_id]

    if len(problems) < original_len:
        _set_data("ideavault_problems", problems)

        # Remove related links (cascade)
        links = _get_data("ideavault_problem_idea_links", [])
        links = [l for l in links if l['problem_id'] != problem_id]
        _set_data("ideavault_problem_idea_links", links)

        # Nullify note references (SET NULL behavior)
        notes = _get_data("ideavault_notes", [])
        for note in notes:
            if note.get('problem_id') == problem_id:
                note['problem_id'] = None
        _set_data("ideavault_notes", notes)

        return True
    return False


def get_problems_count_by_status() -> dict:
    """Get count of problems grouped by status."""
    problems = _get_data("ideavault_problems", [])
    counts = {}
    for p in problems:
        status = p.get('status', 'open')
        counts[status] = counts.get(status, 0) + 1
    return counts


def get_recent_problems(limit: int = 5) -> list[dict]:
    """Get most recently added problems."""
    problems = get_all_problems()
    return problems[:limit]


# =============================================================================
# IDEAS CRUD
# =============================================================================

def create_idea(title: str, pitch: str = "", target_user: str = "", value_prop: str = "",
                differentiation: str = "", assumptions: str = "", risks: str = "",
                status: str = "new", score: Optional[int] = None, tags: str = "") -> int:
    """Create a new idea and return its ID."""
    ideas = _get_data("ideavault_ideas", [])
    now = datetime.now().isoformat()
    idea_id = _get_next_id("ideas")

    idea = {
        "id": idea_id,
        "title": title,
        "pitch": pitch,
        "target_user": target_user,
        "value_prop": value_prop,
        "differentiation": differentiation,
        "assumptions": assumptions,
        "risks": risks,
        "status": status,
        "score": score,
        "tags": tags,
        "created_at": now,
        "updated_at": now
    }

    ideas.append(idea)
    _set_data("ideavault_ideas", ideas)
    return idea_id


def get_all_ideas() -> list[dict]:
    """Get all ideas as a list of dicts."""
    ideas = _get_data("ideavault_ideas", [])
    return sorted(ideas, key=lambda x: x.get('created_at', ''), reverse=True)


def get_idea_by_id(idea_id: int) -> Optional[dict]:
    """Get a single idea by ID."""
    ideas = _get_data("ideavault_ideas", [])
    for i in ideas:
        if i['id'] == idea_id:
            return i
    return None


def update_idea(idea_id: int, title: str, pitch: str, target_user: str, value_prop: str,
                differentiation: str, assumptions: str, risks: str, status: str,
                score: Optional[int], tags: str) -> bool:
    """Update an existing idea."""
    ideas = _get_data("ideavault_ideas", [])
    now = datetime.now().isoformat()

    for i, idea in enumerate(ideas):
        if idea['id'] == idea_id:
            ideas[i].update({
                "title": title,
                "pitch": pitch,
                "target_user": target_user,
                "value_prop": value_prop,
                "differentiation": differentiation,
                "assumptions": assumptions,
                "risks": risks,
                "status": status,
                "score": score,
                "tags": tags,
                "updated_at": now
            })
            _set_data("ideavault_ideas", ideas)
            return True
    return False


def delete_idea(idea_id: int) -> bool:
    """Delete an idea by ID (also removes related links and nullifies note references)."""
    ideas = _get_data("ideavault_ideas", [])
    original_len = len(ideas)
    ideas = [i for i in ideas if i['id'] != idea_id]

    if len(ideas) < original_len:
        _set_data("ideavault_ideas", ideas)

        # Remove related links (cascade)
        links = _get_data("ideavault_problem_idea_links", [])
        links = [l for l in links if l['idea_id'] != idea_id]
        _set_data("ideavault_problem_idea_links", links)

        # Nullify note references (SET NULL behavior)
        notes = _get_data("ideavault_notes", [])
        for note in notes:
            if note.get('idea_id') == idea_id:
                note['idea_id'] = None
        _set_data("ideavault_notes", notes)

        return True
    return False


def get_ideas_count_by_status() -> dict:
    """Get count of ideas grouped by status."""
    ideas = _get_data("ideavault_ideas", [])
    counts = {}
    for i in ideas:
        status = i.get('status', 'new')
        counts[status] = counts.get(status, 0) + 1
    return counts


def get_recent_ideas(limit: int = 5) -> list[dict]:
    """Get most recently added ideas."""
    ideas = get_all_ideas()
    return ideas[:limit]


# =============================================================================
# PROBLEM-IDEA LINKS
# =============================================================================

def link_problem_to_idea(problem_id: int, idea_id: int) -> bool:
    """Create a link between a problem and an idea."""
    links = _get_data("ideavault_problem_idea_links", [])

    # Check if link already exists
    for l in links:
        if l['problem_id'] == problem_id and l['idea_id'] == idea_id:
            return False  # Already exists

    link_id = _get_next_id("links")
    links.append({
        "id": link_id,
        "problem_id": problem_id,
        "idea_id": idea_id
    })
    _set_data("ideavault_problem_idea_links", links)
    return True


def unlink_problem_from_idea(problem_id: int, idea_id: int) -> bool:
    """Remove a link between a problem and an idea."""
    links = _get_data("ideavault_problem_idea_links", [])
    original_len = len(links)
    links = [l for l in links if not (l['problem_id'] == problem_id and l['idea_id'] == idea_id)]

    if len(links) < original_len:
        _set_data("ideavault_problem_idea_links", links)
        return True
    return False


def get_ideas_for_problem(problem_id: int) -> list[dict]:
    """Get all ideas linked to a problem."""
    links = _get_data("ideavault_problem_idea_links", [])
    idea_ids = [l['idea_id'] for l in links if l['problem_id'] == problem_id]

    ideas = _get_data("ideavault_ideas", [])
    return [i for i in ideas if i['id'] in idea_ids]


def get_problems_for_idea(idea_id: int) -> list[dict]:
    """Get all problems linked to an idea."""
    links = _get_data("ideavault_problem_idea_links", [])
    problem_ids = [l['problem_id'] for l in links if l['idea_id'] == idea_id]

    problems = _get_data("ideavault_problems", [])
    return [p for p in problems if p['id'] in problem_ids]


def get_linked_problem_ids_for_idea(idea_id: int) -> list[int]:
    """Get IDs of all problems linked to an idea."""
    links = _get_data("ideavault_problem_idea_links", [])
    return [l['problem_id'] for l in links if l['idea_id'] == idea_id]


def set_problem_links_for_idea(idea_id: int, problem_ids: list[int]):
    """Set the problem links for an idea (replaces existing links)."""
    links = _get_data("ideavault_problem_idea_links", [])

    # Remove existing links for this idea
    links = [l for l in links if l['idea_id'] != idea_id]

    # Add new links
    for pid in problem_ids:
        link_id = _get_next_id("links")
        links.append({
            "id": link_id,
            "problem_id": pid,
            "idea_id": idea_id
        })

    _set_data("ideavault_problem_idea_links", links)


# =============================================================================
# NOTES CRUD
# =============================================================================

def create_note(note_type: str, content: str, links: str = "",
                problem_id: Optional[int] = None, idea_id: Optional[int] = None) -> int:
    """Create a new note and return its ID."""
    notes = _get_data("ideavault_notes", [])
    now = datetime.now().isoformat()
    note_id = _get_next_id("notes")

    note = {
        "id": note_id,
        "note_type": note_type,
        "content": content,
        "links": links,
        "problem_id": problem_id,
        "idea_id": idea_id,
        "created_at": now
    }

    notes.append(note)
    _set_data("ideavault_notes", notes)
    return note_id


def get_all_notes() -> list[dict]:
    """Get all notes as a list of dicts."""
    notes = _get_data("ideavault_notes", [])
    return sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)


def get_note_by_id(note_id: int) -> Optional[dict]:
    """Get a single note by ID."""
    notes = _get_data("ideavault_notes", [])
    for n in notes:
        if n['id'] == note_id:
            return n
    return None


def update_note(note_id: int, note_type: str, content: str, links: str,
                problem_id: Optional[int], idea_id: Optional[int]) -> bool:
    """Update an existing note."""
    notes = _get_data("ideavault_notes", [])

    for i, n in enumerate(notes):
        if n['id'] == note_id:
            notes[i].update({
                "note_type": note_type,
                "content": content,
                "links": links,
                "problem_id": problem_id,
                "idea_id": idea_id
            })
            _set_data("ideavault_notes", notes)
            return True
    return False


def delete_note(note_id: int) -> bool:
    """Delete a note by ID."""
    notes = _get_data("ideavault_notes", [])
    original_len = len(notes)
    notes = [n for n in notes if n['id'] != note_id]

    if len(notes) < original_len:
        _set_data("ideavault_notes", notes)
        return True
    return False


def get_notes_for_problem(problem_id: int) -> list[dict]:
    """Get all notes attached to a problem."""
    notes = _get_data("ideavault_notes", [])
    result = [n for n in notes if n.get('problem_id') == problem_id]
    return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)


def get_notes_for_idea(idea_id: int) -> list[dict]:
    """Get all notes attached to an idea."""
    notes = _get_data("ideavault_notes", [])
    result = [n for n in notes if n.get('idea_id') == idea_id]
    return sorted(result, key=lambda x: x.get('created_at', ''), reverse=True)


# =============================================================================
# DATA EXPORT/IMPORT (for backup/restore)
# =============================================================================

def export_all_data() -> dict:
    """Export all data for backup purposes."""
    return {
        "problems": _get_data("ideavault_problems", []),
        "ideas": _get_data("ideavault_ideas", []),
        "notes": _get_data("ideavault_notes", []),
        "links": _get_data("ideavault_problem_idea_links", []),
        "counters": {
            "problems": _get_data("ideavault_counter_problems", 0),
            "ideas": _get_data("ideavault_counter_ideas", 0),
            "notes": _get_data("ideavault_counter_notes", 0),
            "links": _get_data("ideavault_counter_links", 0),
        }
    }


def import_all_data(data: dict) -> bool:
    """Import data from a backup."""
    try:
        if "problems" in data:
            _set_data("ideavault_problems", data["problems"])
        if "ideas" in data:
            _set_data("ideavault_ideas", data["ideas"])
        if "notes" in data:
            _set_data("ideavault_notes", data["notes"])
        if "links" in data:
            _set_data("ideavault_problem_idea_links", data["links"])
        if "counters" in data:
            for key, val in data["counters"].items():
                _set_data(f"ideavault_counter_{key}", val)
        return True
    except Exception:
        return False


def clear_all_data():
    """Clear all data from local storage."""
    _set_data("ideavault_problems", [])
    _set_data("ideavault_ideas", [])
    _set_data("ideavault_notes", [])
    _set_data("ideavault_problem_idea_links", [])
    _set_data("ideavault_counter_problems", 0)
    _set_data("ideavault_counter_ideas", 0)
    _set_data("ideavault_counter_notes", 0)
    _set_data("ideavault_counter_links", 0)
