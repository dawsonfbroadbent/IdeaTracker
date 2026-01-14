"""
Database module for Idea Vault - PostgreSQL (Supabase) CRUD operations.
"""
import os
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional


def get_connection():
    """Get a database connection from Supabase credentials."""
    # Try Streamlit secrets first (for Streamlit Cloud), then environment variables
    try:
        db_url = st.secrets["DATABASE_URL"]
    except Exception:
        db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        raise ValueError(
            "DATABASE_URL not found. Set it in .streamlit/secrets.toml or as an environment variable."
        )

    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn


def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Problems table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            observed_context TEXT,
            severity INTEGER CHECK(severity >= 1 AND severity <= 5),
            frequency TEXT CHECK(frequency IN ('rare', 'weekly', 'daily')),
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'solved', 'ignored')),
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ideas table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            pitch TEXT,
            target_user TEXT,
            value_prop TEXT,
            differentiation TEXT,
            assumptions TEXT,
            risks TEXT,
            status TEXT DEFAULT 'new' CHECK(status IN ('new', 'researching', 'validating', 'building', 'parked')),
            score INTEGER CHECK(score IS NULL OR (score >= 0 AND score <= 100)),
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Problem-Idea links (many-to-many)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problem_idea_links (
            id SERIAL PRIMARY KEY,
            problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
            idea_id INTEGER NOT NULL REFERENCES ideas(id) ON DELETE CASCADE,
            UNIQUE(problem_id, idea_id)
        )
    """)

    # Notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            note_type TEXT CHECK(note_type IN ('interview', 'competitor', 'pricing', 'tech', 'general')),
            content TEXT NOT NULL,
            links TEXT,
            problem_id INTEGER REFERENCES problems(id) ON DELETE SET NULL,
            idea_id INTEGER REFERENCES ideas(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# =============================================================================
# PROBLEMS CRUD
# =============================================================================

def create_problem(title: str, description: str = "", observed_context: str = "",
                   severity: int = 3, frequency: str = "weekly", status: str = "open",
                   tags: str = "") -> int:
    """Create a new problem and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO problems (title, description, observed_context, severity, frequency, status, tags, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (title, description, observed_context, severity, frequency, status, tags, now, now))
    problem_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return problem_id


def get_all_problems() -> list[dict]:
    """Get all problems as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_problem_by_id(problem_id: int) -> Optional[dict]:
    """Get a single problem by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems WHERE id = %s", (problem_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_problem(problem_id: int, title: str, description: str, observed_context: str,
                   severity: int, frequency: str, status: str, tags: str) -> bool:
    """Update an existing problem."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        UPDATE problems
        SET title = %s, description = %s, observed_context = %s, severity = %s,
            frequency = %s, status = %s, tags = %s, updated_at = %s
        WHERE id = %s
    """, (title, description, observed_context, severity, frequency, status, tags, now, problem_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_problem(problem_id: int) -> bool:
    """Delete a problem by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problems WHERE id = %s", (problem_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_problems_count_by_status() -> dict:
    """Get count of problems grouped by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM problems GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    return {row['status']: row['count'] for row in rows}


def get_recent_problems(limit: int = 5) -> list[dict]:
    """Get most recently added problems."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM problems ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# =============================================================================
# IDEAS CRUD
# =============================================================================

def create_idea(title: str, pitch: str = "", target_user: str = "", value_prop: str = "",
                differentiation: str = "", assumptions: str = "", risks: str = "",
                status: str = "new", score: Optional[int] = None, tags: str = "") -> int:
    """Create a new idea and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO ideas (title, pitch, target_user, value_prop, differentiation, assumptions, risks, status, score, tags, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (title, pitch, target_user, value_prop, differentiation, assumptions, risks, status, score, tags, now, now))
    idea_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return idea_id


def get_all_ideas() -> list[dict]:
    """Get all ideas as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ideas ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_idea_by_id(idea_id: int) -> Optional[dict]:
    """Get a single idea by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ideas WHERE id = %s", (idea_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_idea(idea_id: int, title: str, pitch: str, target_user: str, value_prop: str,
                differentiation: str, assumptions: str, risks: str, status: str,
                score: Optional[int], tags: str) -> bool:
    """Update an existing idea."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        UPDATE ideas
        SET title = %s, pitch = %s, target_user = %s, value_prop = %s, differentiation = %s,
            assumptions = %s, risks = %s, status = %s, score = %s, tags = %s, updated_at = %s
        WHERE id = %s
    """, (title, pitch, target_user, value_prop, differentiation, assumptions, risks, status, score, tags, now, idea_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_idea(idea_id: int) -> bool:
    """Delete an idea by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ideas WHERE id = %s", (idea_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_ideas_count_by_status() -> dict:
    """Get count of ideas grouped by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM ideas GROUP BY status")
    rows = cursor.fetchall()
    conn.close()
    return {row['status']: row['count'] for row in rows}


def get_recent_ideas(limit: int = 5) -> list[dict]:
    """Get most recently added ideas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ideas ORDER BY created_at DESC LIMIT %s", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# =============================================================================
# PROBLEM-IDEA LINKS
# =============================================================================

def link_problem_to_idea(problem_id: int, idea_id: int) -> bool:
    """Create a link between a problem and an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO problem_idea_links (problem_id, idea_id) VALUES (%s, %s)
        """, (problem_id, idea_id))
        conn.commit()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        conn.close()
        return False


def unlink_problem_from_idea(problem_id: int, idea_id: int) -> bool:
    """Remove a link between a problem and an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM problem_idea_links WHERE problem_id = %s AND idea_id = %s
    """, (problem_id, idea_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_ideas_for_problem(problem_id: int) -> list[dict]:
    """Get all ideas linked to a problem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.* FROM ideas i
        JOIN problem_idea_links pil ON i.id = pil.idea_id
        WHERE pil.problem_id = %s
    """, (problem_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_problems_for_idea(idea_id: int) -> list[dict]:
    """Get all problems linked to an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.* FROM problems p
        JOIN problem_idea_links pil ON p.id = pil.problem_id
        WHERE pil.idea_id = %s
    """, (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_linked_problem_ids_for_idea(idea_id: int) -> list[int]:
    """Get IDs of all problems linked to an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT problem_id FROM problem_idea_links WHERE idea_id = %s", (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row['problem_id'] for row in rows]


def set_problem_links_for_idea(idea_id: int, problem_ids: list[int]):
    """Set the problem links for an idea (replaces existing links)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problem_idea_links WHERE idea_id = %s", (idea_id,))
    for pid in problem_ids:
        cursor.execute("INSERT INTO problem_idea_links (problem_id, idea_id) VALUES (%s, %s)", (pid, idea_id))
    conn.commit()
    conn.close()


# =============================================================================
# NOTES CRUD
# =============================================================================

def create_note(note_type: str, content: str, links: str = "",
                problem_id: Optional[int] = None, idea_id: Optional[int] = None) -> int:
    """Create a new note and return its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("""
        INSERT INTO notes (note_type, content, links, problem_id, idea_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (note_type, content, links, problem_id, idea_id, now))
    note_id = cursor.fetchone()['id']
    conn.commit()
    conn.close()
    return note_id


def get_all_notes() -> list[dict]:
    """Get all notes as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_note_by_id(note_id: int) -> Optional[dict]:
    """Get a single note by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_note(note_id: int, note_type: str, content: str, links: str,
                problem_id: Optional[int], idea_id: Optional[int]) -> bool:
    """Update an existing note."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE notes
        SET note_type = %s, content = %s, links = %s, problem_id = %s, idea_id = %s
        WHERE id = %s
    """, (note_type, content, links, problem_id, idea_id, note_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_note(note_id: int) -> bool:
    """Delete a note by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_notes_for_problem(problem_id: int) -> list[dict]:
    """Get all notes attached to a problem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE problem_id = %s ORDER BY created_at DESC", (problem_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_notes_for_idea(idea_id: int) -> list[dict]:
    """Get all notes attached to an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE idea_id = %s ORDER BY created_at DESC", (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
