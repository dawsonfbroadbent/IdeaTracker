'use client';

import { useState, useEffect } from 'react';
import {
  getAllIdeas,
  getIdeaById,
  createIdea,
  updateIdea,
  deleteIdea,
  getAllProblems,
  getProblemsForIdea,
  getNotesForIdea,
  getLinkedProblemIdsForIdea,
  setProblemLinksForIdea,
} from '@/lib/storage';
import { Idea, Problem, Note } from '@/lib/types';

export default function Ideas() {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [filteredIdeas, setFilteredIdeas] = useState<Idea[]>([]);
  const [allProblems, setAllProblems] = useState<Problem[]>([]);
  const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);
  const [linkedProblems, setLinkedProblems] = useState<Problem[]>([]);
  const [linkedNotes, setLinkedNotes] = useState<Note[]>([]);
  const [isEditing, setIsEditing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Filters
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterTags, setFilterTags] = useState('');
  const [keyword, setKeyword] = useState('');

  // Form state
  const [form, setForm] = useState({
    title: '',
    pitch: '',
    target_user: '',
    value_prop: '',
    differentiation: '',
    assumptions: '',
    risks: '',
    status: 'new' as Idea['status'],
    score: null as number | null,
    useScore: false,
    tags: '',
    linkedProblemIds: [] as number[],
  });

  useEffect(() => {
    setMounted(true);
    loadData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [ideas, filterStatus, filterTags, keyword]);

  const loadData = () => {
    setIdeas(getAllIdeas());
    setAllProblems(getAllProblems());
  };

  const applyFilters = () => {
    let filtered = [...ideas];

    if (filterStatus !== 'All') {
      filtered = filtered.filter((i) => i.status === filterStatus);
    }
    if (filterTags) {
      const tags = filterTags.toLowerCase().split(',').map((t) => t.trim());
      filtered = filtered.filter(
        (i) => i.tags && tags.some((t) => i.tags.toLowerCase().includes(t))
      );
    }
    if (keyword) {
      const kw = keyword.toLowerCase();
      filtered = filtered.filter(
        (i) =>
          i.title.toLowerCase().includes(kw) ||
          i.pitch.toLowerCase().includes(kw)
      );
    }

    setFilteredIdeas(filtered);
  };

  const selectIdea = (id: number) => {
    const idea = getIdeaById(id);
    if (idea) {
      setSelectedIdea(idea);
      setLinkedProblems(getProblemsForIdea(id));
      setLinkedNotes(getNotesForIdea(id));
      setIsEditing(false);
      setShowForm(false);
    }
  };

  const startEdit = () => {
    if (selectedIdea) {
      const linkedIds = getLinkedProblemIdsForIdea(selectedIdea.id);
      setForm({
        title: selectedIdea.title,
        pitch: selectedIdea.pitch,
        target_user: selectedIdea.target_user,
        value_prop: selectedIdea.value_prop,
        differentiation: selectedIdea.differentiation,
        assumptions: selectedIdea.assumptions,
        risks: selectedIdea.risks,
        status: selectedIdea.status,
        score: selectedIdea.score,
        useScore: selectedIdea.score !== null,
        tags: selectedIdea.tags,
        linkedProblemIds: linkedIds,
      });
      setIsEditing(true);
      setShowForm(true);
    }
  };

  const startNew = () => {
    setSelectedIdea(null);
    setForm({
      title: '',
      pitch: '',
      target_user: '',
      value_prop: '',
      differentiation: '',
      assumptions: '',
      risks: '',
      status: 'new',
      score: null,
      useScore: false,
      tags: '',
      linkedProblemIds: [],
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

    const finalScore = form.useScore ? (form.score ?? 50) : null;

    if (isEditing && selectedIdea) {
      updateIdea(
        selectedIdea.id,
        form.title.trim(),
        form.pitch,
        form.target_user,
        form.value_prop,
        form.differentiation,
        form.assumptions,
        form.risks,
        form.status,
        finalScore,
        form.tags
      );
      setProblemLinksForIdea(selectedIdea.id, form.linkedProblemIds);
    } else {
      const id = createIdea(
        form.title.trim(),
        form.pitch,
        form.target_user,
        form.value_prop,
        form.differentiation,
        form.assumptions,
        form.risks,
        form.status,
        finalScore,
        form.tags
      );
      setProblemLinksForIdea(id, form.linkedProblemIds);
    }

    loadData();
    setShowForm(false);
    setSelectedIdea(null);
  };

  const handleDelete = () => {
    if (selectedIdea) {
      deleteIdea(selectedIdea.id);
      loadData();
      setSelectedIdea(null);
      setConfirmDelete(false);
    }
  };

  const toggleProblemLink = (problemId: number) => {
    setForm((prev) => ({
      ...prev,
      linkedProblemIds: prev.linkedProblemIds.includes(problemId)
        ? prev.linkedProblemIds.filter((id) => id !== problemId)
        : [...prev.linkedProblemIds, problemId],
    }));
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
        <h1 className="text-3xl font-bold">💡 Ideas</h1>
        <button onClick={startNew} className="btn btn-primary">
          + Add Idea
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
                <label className="label">Status</label>
                <select
                  className="input"
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <option>All</option>
                  <option value="new">new</option>
                  <option value="researching">researching</option>
                  <option value="validating">validating</option>
                  <option value="building">building</option>
                  <option value="parked">parked</option>
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

          {/* Idea List */}
          {filteredIdeas.length > 0 ? (
            <div className="card">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Title</th>
                    <th className="text-left py-2">Pitch</th>
                    <th className="text-left py-2">Status</th>
                    <th className="text-center py-2">Score</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredIdeas.map((i) => (
                    <tr
                      key={i.id}
                      className={`border-b cursor-pointer hover:bg-gray-50 ${
                        selectedIdea?.id === i.id ? 'bg-blue-50' : ''
                      }`}
                      onClick={() => selectIdea(i.id)}
                    >
                      <td className="py-2 font-medium">{i.title}</td>
                      <td className="py-2 text-gray-500 text-sm">
                        {i.pitch.slice(0, 40)}
                        {i.pitch.length > 40 ? '...' : ''}
                      </td>
                      <td className="py-2">
                        <span className={`badge badge-${i.status}`}>
                          {i.status}
                        </span>
                      </td>
                      <td className="py-2 text-center">
                        {i.score !== null ? i.score : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="card text-center text-gray-500">
              No ideas found. Click &quot;Add Idea&quot; to create one.
            </div>
          )}
        </div>

        {/* Right: Details / Form */}
        <div>
          {showForm ? (
            <div className="card max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-semibold mb-4">
                {isEditing ? 'Edit Idea' : 'New Idea'}
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
                  <label className="label">Pitch (1 sentence)</label>
                  <input
                    type="text"
                    className="input"
                    value={form.pitch}
                    onChange={(e) => setForm({ ...form, pitch: e.target.value })}
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Target User</label>
                  <input
                    type="text"
                    className="input"
                    value={form.target_user}
                    onChange={(e) =>
                      setForm({ ...form, target_user: e.target.value })
                    }
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Value Proposition</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={form.value_prop}
                    onChange={(e) =>
                      setForm({ ...form, value_prop: e.target.value })
                    }
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Differentiation</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={form.differentiation}
                    onChange={(e) =>
                      setForm({ ...form, differentiation: e.target.value })
                    }
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Assumptions</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={form.assumptions}
                    onChange={(e) =>
                      setForm({ ...form, assumptions: e.target.value })
                    }
                  />
                </div>
                <div className="mb-4">
                  <label className="label">Risks</label>
                  <textarea
                    className="input"
                    rows={2}
                    value={form.risks}
                    onChange={(e) => setForm({ ...form, risks: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="label">Status</label>
                    <select
                      className="input"
                      value={form.status}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          status: e.target.value as Idea['status'],
                        })
                      }
                    >
                      <option value="new">new</option>
                      <option value="researching">researching</option>
                      <option value="validating">validating</option>
                      <option value="building">building</option>
                      <option value="parked">parked</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Score (0-100)</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={form.useScore}
                        onChange={(e) =>
                          setForm({ ...form, useScore: e.target.checked })
                        }
                      />
                      <input
                        type="number"
                        className="input"
                        min="0"
                        max="100"
                        disabled={!form.useScore}
                        value={form.score ?? 50}
                        onChange={(e) =>
                          setForm({ ...form, score: Number(e.target.value) })
                        }
                      />
                    </div>
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
                <div className="mb-4">
                  <label className="label">Link to Problems</label>
                  <div className="border rounded-lg p-2 max-h-32 overflow-y-auto">
                    {allProblems.length > 0 ? (
                      allProblems.map((p) => (
                        <label
                          key={p.id}
                          className="flex items-center gap-2 py-1"
                        >
                          <input
                            type="checkbox"
                            checked={form.linkedProblemIds.includes(p.id)}
                            onChange={() => toggleProblemLink(p.id)}
                          />
                          <span className="text-sm">{p.title}</span>
                        </label>
                      ))
                    ) : (
                      <p className="text-gray-500 text-sm">No problems yet.</p>
                    )}
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
          ) : selectedIdea ? (
            <div className="card max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-semibold mb-4">{selectedIdea.title}</h2>
              <div className="space-y-2 text-sm mb-4">
                <p>
                  <strong>Status:</strong>{' '}
                  <span className={`badge badge-${selectedIdea.status}`}>
                    {selectedIdea.status}
                  </span>
                </p>
                <p>
                  <strong>Score:</strong>{' '}
                  {selectedIdea.score !== null ? selectedIdea.score : 'N/A'}
                </p>
                <p>
                  <strong>Target User:</strong>{' '}
                  {selectedIdea.target_user || 'N/A'}
                </p>
                <p>
                  <strong>Tags:</strong> {selectedIdea.tags || 'None'}
                </p>
              </div>

              {selectedIdea.pitch && (
                <div className="mb-3">
                  <strong className="text-sm">Pitch:</strong>
                  <p className="text-gray-600 text-sm">{selectedIdea.pitch}</p>
                </div>
              )}

              {selectedIdea.value_prop && (
                <div className="mb-3">
                  <strong className="text-sm">Value Proposition:</strong>
                  <p className="text-gray-600 text-sm">
                    {selectedIdea.value_prop}
                  </p>
                </div>
              )}

              {selectedIdea.differentiation && (
                <div className="mb-3">
                  <strong className="text-sm">Differentiation:</strong>
                  <p className="text-gray-600 text-sm">
                    {selectedIdea.differentiation}
                  </p>
                </div>
              )}

              {selectedIdea.assumptions && (
                <div className="mb-3">
                  <strong className="text-sm">Assumptions:</strong>
                  <p className="text-gray-600 text-sm">
                    {selectedIdea.assumptions}
                  </p>
                </div>
              )}

              {selectedIdea.risks && (
                <div className="mb-3">
                  <strong className="text-sm">Risks:</strong>
                  <p className="text-gray-600 text-sm">{selectedIdea.risks}</p>
                </div>
              )}

              <hr className="my-4" />

              <h3 className="font-semibold mb-2">Linked Problems</h3>
              {linkedProblems.length > 0 ? (
                <ul className="text-sm space-y-1 mb-4">
                  {linkedProblems.map((p) => (
                    <li key={p.id}>
                      • {p.title}{' '}
                      <span className={`badge badge-${p.status}`}>
                        {p.status}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 text-sm mb-4">No linked problems.</p>
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
                    Are you sure you want to delete this idea?
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
              Select an idea to view details.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
