'use client';

import { useState, useEffect } from 'react';
import {
  getAllProblems,
  getProblemById,
  createProblem,
  updateProblem,
  deleteProblem,
  getIdeasForProblem,
  getNotesForProblem,
} from '@/lib/storage';
import { Problem, Idea, Note } from '@/lib/types';

export default function Problems() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [filteredProblems, setFilteredProblems] = useState<Problem[]>([]);
  const [selectedProblem, setSelectedProblem] = useState<Problem | null>(null);
  const [linkedIdeas, setLinkedIdeas] = useState<Idea[]>([]);
  const [linkedNotes, setLinkedNotes] = useState<Note[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Filters
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterSeverity, setFilterSeverity] = useState('All');
  const [filterTags, setFilterTags] = useState('');
  const [keyword, setKeyword] = useState('');

  // Form state
  const [form, setForm] = useState({
    title: '',
    description: '',
    observed_context: '',
    severity: 3,
    frequency: 'weekly' as Problem['frequency'],
    status: 'open' as Problem['status'],
    tags: '',
  });

  useEffect(() => {
    setMounted(true);
    loadProblems();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [problems, filterStatus, filterSeverity, filterTags, keyword]);

  const loadProblems = () => {
    setProblems(getAllProblems());
  };

  const applyFilters = () => {
    let filtered = [...problems];

    if (filterStatus !== 'All') {
      filtered = filtered.filter((p) => p.status === filterStatus);
    }
    if (filterSeverity !== 'All') {
      filtered = filtered.filter((p) => p.severity === Number(filterSeverity));
    }
    if (filterTags) {
      const tags = filterTags.toLowerCase().split(',').map((t) => t.trim());
      filtered = filtered.filter(
        (p) => p.tags && tags.some((t) => p.tags.toLowerCase().includes(t))
      );
    }
    if (keyword) {
      const kw = keyword.toLowerCase();
      filtered = filtered.filter(
        (p) =>
          p.title.toLowerCase().includes(kw) ||
          p.description.toLowerCase().includes(kw)
      );
    }

    setFilteredProblems(filtered);
  };

  const selectProblem = (id: number) => {
    const problem = getProblemById(id);
    if (problem) {
      setSelectedProblem(problem);
      setLinkedIdeas(getIdeasForProblem(id));
      setLinkedNotes(getNotesForProblem(id));
      setIsEditing(false);
      setShowForm(false);
    }
  };

  const startEdit = () => {
    if (selectedProblem) {
      setForm({
        title: selectedProblem.title,
        description: selectedProblem.description,
        observed_context: selectedProblem.observed_context,
        severity: selectedProblem.severity,
        frequency: selectedProblem.frequency,
        status: selectedProblem.status,
        tags: selectedProblem.tags,
      });
      setIsEditing(true);
      setShowForm(true);
    }
  };

  const startNew = () => {
    setSelectedProblem(null);
    setForm({
      title: '',
      description: '',
      observed_context: '',
      severity: 3,
      frequency: 'weekly',
      status: 'open',
      tags: '',
    });
    setIsEditing(false);
    setShowForm(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) {
      alert('Title is required!');
      return;
    }

    if (isEditing && selectedProblem) {
      updateProblem(
        selectedProblem.id,
        form.title.trim(),
        form.description,
        form.observed_context,
        form.severity,
        form.frequency,
        form.status,
        form.tags
      );
    } else {
      createProblem(
        form.title.trim(),
        form.description,
        form.observed_context,
        form.severity,
        form.frequency,
        form.status,
        form.tags
      );
    }

    loadProblems();
    setShowForm(false);
    setSelectedProblem(null);
  };

  const handleDelete = () => {
    if (selectedProblem) {
      deleteProblem(selectedProblem.id);
      loadProblems();
      setSelectedProblem(null);
      setConfirmDelete(false);
    }
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
        <h1 className="text-3xl font-bold">🔍 Problems</h1>
        <button onClick={startNew} className="btn btn-primary">
          + Add Problem
        </button>
      </div>
      <hr className="mb-6" />

      <div className="grid grid-cols-3 gap-6">
        {/* Left: List */}
        <div className="col-span-2">
          {/* Filters */}
          <div className="card mb-6">
            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="label">Status</label>
                <select
                  className="input"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option>All</option>
                  <option value="open">open</option>
                  <option value="solved">solved</option>
                  <option value="ignored">ignored</option>
                </select>
              </div>
              <div>
                <label className="label">Severity</label>
                <select
                  className="input"
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                >
                  <option>All</option>
                  {[1, 2, 3, 4, 5].map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Tags</label>
                <input
                  type="text"
                  className="input"
                  placeholder="comma-separated"
                  value={filterTags}
                  onChange={(e) => setFilterTags(e.target.value)}
                />
              </div>
              <div>
                <label className="label">Keyword</label>
                <input
                  type="text"
                  className="input"
                  placeholder="Search..."
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Problem List */}
          {filteredProblems.length > 0 ? (
            <div className="card">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Title</th>
                    <th className="text-left py-2">Status</th>
                    <th className="text-center py-2">Severity</th>
                    <th className="text-left py-2">Frequency</th>
                    <th className="text-left py-2">Tags</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProblems.map((p) => (
                    <tr
                      key={p.id}
                      className={`border-b cursor-pointer hover:bg-gray-50 ${
                        selectedProblem?.id === p.id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => selectProblem(p.id)}
                    >
                      <td className="py-2 font-medium">{p.title}</td>
                      <td className="py-2">
                        <span className={`badge badge-${p.status}`}>
                          {p.status}
                        </span>
                      </td>
                      <td className="py-2 text-center">{p.severity}/5</td>
                      <td className="py-2">{p.frequency}</td>
                      <td className="py-2 text-gray-500 text-sm">
                        {p.tags || '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="card text-center text-gray-500">
              No problems found. Click &quot;Add Problem&quot; to create one.
            </div>
          )}
        </div>

        {/* Right: Details / Form */}
        <div>
          {showForm ? (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">
                {isEditing ? 'Edit Problem' : 'New Problem'}
              </h2>
              <form onSubmit={handleSubmit}>
                <div className="mb-4">
                  <label className="label">Title *</label>
                  <input
                    type="text"
                    className="input"
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Description</label>
                  <textarea
                    className="input"
                    rows={3}
                    value={form.description}
                    onChange={(e) =>
                      setForm({ ...form, description: e.target.value })
                    }
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Observed Context</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={form.observed_context}
                    onChange={(e) =>
                      setForm({ ...form, observed_context: e.target.value })
                    }
                  />
                </div>
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div>
                    <label className="label">Severity</label>
                    <select
                      className="input"
                      value={form.severity}
                      onChange={(e) =>
                        setForm({ ...form, severity: Number(e.target.value) })
                      }
                    >
                      {[1, 2, 3, 4, 5].map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="label">Frequency</label>
                    <select
                      className="input"
                      value={form.frequency}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          frequency: e.target.value as Problem['frequency'],
                        })
                      }
                    >
                      <option value="rare">rare</option>
                      <option value="weekly">weekly</option>
                      <option value="daily">daily</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Status</label>
                    <select
                      className="input"
                      value={form.status}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          status: e.target.value as Problem['status'],
                        })
                      }
                    >
                      <option value="open">open</option>
                      <option value="solved">solved</option>
                      <option value="ignored">ignored</option>
                    </select>
                  </div>
                </div>
                <div className="mb-4">
                  <label className="label">Tags (comma-separated)</label>
                  <input
                    type="text"
                    className="input"
                    value={form.tags}
                    onChange={(e) => setForm({ ...form, tags: e.target.value })}
                  />
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
          ) : selectedProblem ? (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">
                {selectedProblem.title}
              </h2>
              <div className="space-y-2 text-sm mb-4">
                <p>
                  <strong>Status:</strong>{' '}
                  <span className={`badge badge-${selectedProblem.status}`}>
                    {selectedProblem.status}
                  </span>
                </p>
                <p>
                  <strong>Severity:</strong> {selectedProblem.severity}/5
                </p>
                <p>
                  <strong>Frequency:</strong> {selectedProblem.frequency}
                </p>
                <p>
                  <strong>Tags:</strong> {selectedProblem.tags || 'None'}
                </p>
                <p>
                  <strong>Created:</strong>{' '}
                  {new Date(selectedProblem.created_at).toLocaleDateString()}
                </p>
              </div>

              {selectedProblem.description && (
                <div className="mb-4">
                  <strong className="text-sm">Description:</strong>
                  <p className="text-gray-600 text-sm mt-1">
                    {selectedProblem.description}
                  </p>
                </div>
              )}

              {selectedProblem.observed_context && (
                <div className="mb-4">
                  <strong className="text-sm">Observed Context:</strong>
                  <p className="text-gray-600 text-sm mt-1">
                    {selectedProblem.observed_context}
                  </p>
                </div>
              )}

              <hr className="my-4" />

              <h3 className="font-semibold mb-2">Linked Ideas</h3>
              {linkedIdeas.length > 0 ? (
                <ul className="text-sm space-y-1 mb-4">
                  {linkedIdeas.map((i) => (
                    <li key={i.id}>
                      • {i.title}{' '}
                      <span className={`badge badge-${i.status}`}>
                        {i.status}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm mb-4">No linked ideas.</p>
              )}

              <h3 className="font-semibold mb-2">Notes</h3>
              {linkedNotes.length > 0 ? (
                <ul className="text-sm space-y-1 mb-4">
                  {linkedNotes.map((n) => (
                    <li key={n.id}>
                      • [{n.note_type}] {n.content.slice(0, 50)}...
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm mb-4">No notes.</p>
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
                    Are you sure you want to delete this problem?
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
              Select a problem to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
