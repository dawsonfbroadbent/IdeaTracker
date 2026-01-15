'use client';

import { useState, useEffect } from 'react';
import {
  getAllNotes,
  getNoteById,
  createNote,
  updateNote,
  deleteNote,
  getAllProblems,
  getAllIdeas,
  getProblemById,
  getIdeaById,
} from '@/lib/storage';
import { Note, Problem, Idea } from '@/lib/types';

export default function Notes() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [filteredNotes, setFilteredNotes] = useState<Note[]>([]);
  const [allProblems, setAllProblems] = useState<Problem[]>([]);
  const [allIdeas, setAllIdeas] = useState<Idea[]>([]);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Filters
  const [filterType, setFilterType] = useState('All');
  const [filterProblem, setFilterProblem] = useState<number | null>(null);
  const [filterIdea, setFilterIdea] = useState<number | null>(null);

  // Form state
  const [form, setForm] = useState({
    note_type: 'general' as Note['note_type'],
    content: '',
    links: '',
    problem_id: null as number | null,
    idea_id: null as number | null,
  });

  useEffect(() => {
    setMounted(true);
    loadData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [notes, filterType, filterProblem, filterIdea]);

  const loadData = () => {
    setNotes(getAllNotes());
    setAllProblems(getAllProblems());
    setAllIdeas(getAllIdeas());
  };

  const applyFilters = () => {
    let filtered = [...notes];

    if (filterType !== 'All') {
      filtered = filtered.filter((n) => n.note_type === filterType);
    }
    if (filterProblem !== null) {
      filtered = filtered.filter((n) => n.problem_id === filterProblem);
    }
    if (filterIdea !== null) {
      filtered = filtered.filter((n) => n.idea_id === filterIdea);
    }

    setFilteredNotes(filtered);
  };

  const selectNote = (id: number) => {
    const note = getNoteById(id);
    if (note) {
      setSelectedNote(note);
      setIsEditing(false);
      setShowForm(false);
    }
  };

  const startEdit = () => {
    if (selectedNote) {
      setForm({
        note_type: selectedNote.note_type,
        content: selectedNote.content,
        links: selectedNote.links,
        problem_id: selectedNote.problem_id,
        idea_id: selectedNote.idea_id,
      });
      setIsEditing(true);
      setShowForm(true);
    }
  };

  const startNew = () => {
    setSelectedNote(null);
    setForm({
      note_type: 'general',
      content: '',
      links: '',
      problem_id: null,
      idea_id: null,
    });
    setIsEditing(false);
    setShowForm(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.content.trim()) {
      alert('Content is required!');
      return;
    }

    if (isEditing && selectedNote) {
      updateNote(
        selectedNote.id,
        form.note_type,
        form.content.trim(),
        form.links,
        form.problem_id,
        form.idea_id
      );
    } else {
      createNote(
        form.note_type,
        form.content.trim(),
        form.links,
        form.problem_id,
        form.idea_id
      );
    }

    loadData();
    setShowForm(false);
    setSelectedNote(null);
  };

  const handleDelete = () => {
    if (selectedNote) {
      deleteNote(selectedNote.id);
      loadData();
      setSelectedNote(null);
      setConfirmDelete(false);
    }
  };

  const getProblemName = (id: number | null) => {
    if (!id) return '-';
    const p = getProblemById(id);
    return p ? p.title : '-';
  };

  const getIdeaName = (id: number | null) => {
    if (!id) return '-';
    const i = getIdeaById(id);
    return i ? i.title : '-';
  };

  if (!mounted) {
    return (
      <div className="p-8">
        <div className="animate-pulse">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">📝 Notes</h1>
        <button onClick={startNew} className="btn btn-primary">
          + Add Note
        </button>
      </div>
      <hr className="mb-6" />

      <div className="grid grid-cols-3 gap-6">
        {/* Left: List */}
        <div className="col-span-2">
          {/* Filters */}
          <div className="card mb-6">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="label">Type</label>
                <select
                  className="input"
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                >
                  <option>All</option>
                  <option value="interview">interview</option>
                  <option value="competitor">competitor</option>
                  <option value="pricing">pricing</option>
                  <option value="tech">tech</option>
                  <option value="general">general</option>
                </select>
              </div>
              <div>
                <label className="label">Problem</label>
                <select
                  className="input"
                  value={filterProblem ?? ''}
                  onChange={(e) =>
                    setFilterProblem(
                      e.target.value ? Number(e.target.value) : null
                    )
                  }
                >
                  <option value="">All</option>
                  {allProblems.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.title.slice(0, 30)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Idea</label>
                <select
                  className="input"
                  value={filterIdea ?? ''}
                  onChange={(e) =>
                    setFilterIdea(e.target.value ? Number(e.target.value) : null)
                  }
                >
                  <option value="">All</option>
                  {allIdeas.map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.title.slice(0, 30)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Notes List */}
          {filteredNotes.length > 0 ? (
            <div className="card">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Type</th>
                    <th className="text-left py-2">Content</th>
                    <th className="text-left py-2">Problem</th>
                    <th className="text-left py-2">Idea</th>
                    <th className="text-left py-2">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredNotes.map((n) => (
                    <tr
                      key={n.id}
                      className={`border-b cursor-pointer hover:bg-gray-50 ${
                        selectedNote?.id === n.id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => selectNote(n.id)}
                    >
                      <td className="py-2">
                        <span className="badge bg-gray-100 text-gray-800">
                          {n.note_type}
                        </span>
                      </td>
                      <td className="py-2 text-sm">
                        {n.content.slice(0, 50)}
                        {n.content.length > 50 ? '...' : ''}
                      </td>
                      <td className="py-2 text-sm text-gray-500">
                        {getProblemName(n.problem_id).slice(0, 20)}
                      </td>
                      <td className="py-2 text-sm text-gray-500">
                        {getIdeaName(n.idea_id).slice(0, 20)}
                      </td>
                      <td className="py-2 text-sm text-gray-500">
                        {new Date(n.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="card text-center text-gray-500">
              No notes found. Click &quot;Add Note&quot; to create one.
            </div>
          )}
        </div>

        {/* Right: Details / Form */}
        <div>
          {showForm ? (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">
                {isEditing ? 'Edit Note' : 'New Note'}
              </h2>
              <form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <label className="label">Type *</label>
                  <select
                    className="input"
                    value={form.note_type}
                    onChange={(e) =>
                      setForm({
                        ...form,
                        note_type: e.target.value as Note['note_type'],
                      })
                    }
                  >
                    <option value="interview">interview</option>
                    <option value="competitor">competitor</option>
                    <option value="pricing">pricing</option>
                    <option value="tech">tech</option>
                    <option value="general">general</option>
                  </select>
                </div>
                <div className="mb-4">
                  <label className="label">Content *</label>
                  <textarea
                    className="input"
                    rows={6}
                    value={form.content}
                    onChange={(e) =>
                      setForm({ ...form, content: e.target.value })
                    }
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Links (URLs, references)</label>
                  <input
                    type="text"
                    className="input"
                    value={form.links}
                    onChange={(e) => setForm({ ...form, links: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="label">Attach to Problem</label>
                    <select
                      className="input"
                      value={form.problem_id ?? ''}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          problem_id: e.target.value
                            ? Number(e.target.value)
                            : null,
                        })
                      }
                    >
                      <option value="">None</option>
                      {allProblems.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.title.slice(0, 30)}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="label">Attach to Idea</label>
                    <select
                      className="input"
                      value={form.idea_id ?? ''}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          idea_id: e.target.value
                            ? Number(e.target.value)
                            : null,
                        })
                      }
                    >
                      <option value="">None</option>
                      {allIdeas.map((i) => (
                        <option key={i.id} value={i.id}>
                          {i.title.slice(0, 30)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button type="submit" className="btn btn-primary">
                    Save
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowForm(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : selectedNote ? (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">
                {selectedNote.note_type.toUpperCase()} Note
              </h2>
              <div className="space-y-2 text-sm mb-4">
                <p>
                  <strong>Type:</strong>{' '}
                  <span className="badge bg-gray-100 text-gray-800">
                    {selectedNote.note_type}
                  </span>
                </p>
                <p>
                  <strong>Created:</strong>{' '}
                  {new Date(selectedNote.created_at).toLocaleString()}
                </p>
                {selectedNote.problem_id && (
                  <p>
                    <strong>Problem:</strong>{' '}
                    {getProblemName(selectedNote.problem_id)}
                  </p>
                )}
                {selectedNote.idea_id && (
                  <p>
                    <strong>Idea:</strong> {getIdeaName(selectedNote.idea_id)}
                  </p>
                )}
              </div>

              <div className="mb-4">
                <strong className="text-sm">Content:</strong>
                <div className="mt-2 p-3 bg-gray-50 rounded-lg text-sm whitespace-pre-wrap">
                  {selectedNote.content}
                </div>
              </div>

              {selectedNote.links && (
                <div className="mb-4">
                  <strong className="text-sm">Links:</strong>
                  <p className="text-blue-600 text-sm break-all">
                    {selectedNote.links}
                  </p>
                </div>
              )}

              <div className="flex gap-2">
                <button onClick={startEdit} className="btn btn-primary">
                  Edit
                </button>
                <button
                  onClick={() => setConfirmDelete(true)}
                  className="btn btn-danger"
                >
                  Delete
                </button>
              </div>

              {confirmDelete && (
                <div className="mt-4 p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-800 mb-2">
                    Are you sure you want to delete this note?
                  </p>
                  <div className="flex gap-2">
                    <button onClick={handleDelete} className="btn btn-danger">
                      Yes, Delete
                    </button>
                    <button
                      onClick={() => setConfirmDelete(false)}
                      className="btn btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="card text-center text-gray-500">
              Select a note to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
