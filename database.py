"""
Database module for Idea Vault - SQLite CRUD operations for problems, ideas, notes, and links.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "idea_vault.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Problems table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id INTEGER NOT NULL,
            idea_id INTEGER NOT NULL,
            FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE CASCADE,
            FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE CASCADE,
            UNIQUE(problem_id, idea_id)
        )
    """)

    # Notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_type TEXT CHECK(note_type IN ('interview', 'competitor', 'pricing', 'tech', 'general')),
            content TEXT NOT NULL,
            links TEXT,
            problem_id INTEGER,
            idea_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (problem_id) REFERENCES problems(id) ON DELETE SET NULL,
            FOREIGN KEY (idea_id) REFERENCES ideas(id) ON DELETE SET NULL
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
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO problems (title, description, observed_context, severity, frequency, status, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, description, observed_context, severity, frequency, status, tags, now, now))
    problem_id = cursor.lastrowid
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
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_problem(problem_id: int, title: str, description: str, observed_context: str,
                   severity: int, frequency: str, status: str, tags: str) -> bool:
    """Update an existing problem."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        UPDATE problems
        SET title = ?, description = ?, observed_context = ?, severity = ?,
            frequency = ?, status = ?, tags = ?, updated_at = ?
        WHERE id = ?
    """, (title, description, observed_context, severity, frequency, status, tags, now, problem_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_problem(problem_id: int) -> bool:
    """Delete a problem by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problems WHERE id = ?", (problem_id,))
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
    cursor.execute("SELECT * FROM problems ORDER BY created_at DESC LIMIT ?", (limit,))
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
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO ideas (title, pitch, target_user, value_prop, differentiation, assumptions, risks, status, score, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, pitch, target_user, value_prop, differentiation, assumptions, risks, status, score, tags, now, now))
    idea_id = cursor.lastrowid
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
    cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_idea(idea_id: int, title: str, pitch: str, target_user: str, value_prop: str,
                differentiation: str, assumptions: str, risks: str, status: str,
                score: Optional[int], tags: str) -> bool:
    """Update an existing idea."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        UPDATE ideas
        SET title = ?, pitch = ?, target_user = ?, value_prop = ?, differentiation = ?,
            assumptions = ?, risks = ?, status = ?, score = ?, tags = ?, updated_at = ?
        WHERE id = ?
    """, (title, pitch, target_user, value_prop, differentiation, assumptions, risks, status, score, tags, now, idea_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_idea(idea_id: int) -> bool:
    """Delete an idea by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ideas WHERE id = ?", (idea_id,))
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
    cursor.execute("SELECT * FROM ideas ORDER BY created_at DESC LIMIT ?", (limit,))
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
            INSERT INTO problem_idea_links (problem_id, idea_id) VALUES (?, ?)
        """, (problem_id, idea_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def unlink_problem_from_idea(problem_id: int, idea_id: int) -> bool:
    """Remove a link between a problem and an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM problem_idea_links WHERE problem_id = ? AND idea_id = ?
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
        WHERE pil.problem_id = ?
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
        WHERE pil.idea_id = ?
    """, (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_linked_problem_ids_for_idea(idea_id: int) -> list[int]:
    """Get IDs of all problems linked to an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT problem_id FROM problem_idea_links WHERE idea_id = ?", (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row['problem_id'] for row in rows]


def set_problem_links_for_idea(idea_id: int, problem_ids: list[int]):
    """Set the problem links for an idea (replaces existing links)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problem_idea_links WHERE idea_id = ?", (idea_id,))
    for pid in problem_ids:
        cursor.execute("INSERT INTO problem_idea_links (problem_id, idea_id) VALUES (?, ?)", (pid, idea_id))
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
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO notes (note_type, content, links, problem_id, idea_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (note_type, content, links, problem_id, idea_id, now))
    note_id = cursor.lastrowid
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
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
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
        SET note_type = ?, content = ?, links = ?, problem_id = ?, idea_id = ?
        WHERE id = ?
    """, (note_type, content, links, problem_id, idea_id, note_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_note(note_id: int) -> bool:
    """Delete a note by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_notes_for_problem(problem_id: int) -> list[dict]:
    """Get all notes attached to a problem."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE problem_id = ? ORDER BY created_at DESC", (problem_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_notes_for_idea(idea_id: int) -> list[dict]:
    """Get all notes attached to an idea."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE idea_id = ? ORDER BY created_at DESC", (idea_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Initialize DB on module import
init_db()
