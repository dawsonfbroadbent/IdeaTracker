import { Problem, Idea, Note, ProblemIdeaLink, StorageData } from './types';

const STORAGE_KEY = 'ideavault_data';

function getStorageData(): StorageData {
  if (typeof window === 'undefined') {
    return {
      problems: [],
      ideas: [],
      notes: [],
      links: [],
      counters: { problems: 0, ideas: 0, notes: 0, links: 0 }
    };
  }

  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    const initial: StorageData = {
      problems: [],
      ideas: [],
      notes: [],
      links: [],
      counters: { problems: 0, ideas: 0, notes: 0, links: 0 }
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(initial));
    return initial;
  }
  return JSON.parse(stored);
}

function saveStorageData(data: StorageData): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function getNextId(data: StorageData, type: keyof StorageData['counters']): number {
  data.counters[type]++;
  return data.counters[type];
}

// =============================================================================
// PROBLEMS CRUD
// =============================================================================

export function createProblem(
  title: string,
  description = '',
  observed_context = '',
  severity = 3,
  frequency: Problem['frequency'] = 'weekly',
  status: Problem['status'] = 'open',
  tags = ''
): number {
  const data = getStorageData();
  const now = new Date().toISOString();
  const id = getNextId(data, 'problems');

  const problem: Problem = {
    id,
    title,
    description,
    observed_context,
    severity,
    frequency,
    status,
    tags,
    created_at: now,
    updated_at: now
  };

  data.problems.push(problem);
  saveStorageData(data);
  return id;
}

export function getAllProblems(): Problem[] {
  const data = getStorageData();
  return [...data.problems].sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

export function getProblemById(id: number): Problem | null {
  const data = getStorageData();
  return data.problems.find(p => p.id === id) || null;
}

export function updateProblem(
  id: number,
  title: string,
  description: string,
  observed_context: string,
  severity: number,
  frequency: Problem['frequency'],
  status: Problem['status'],
  tags: string
): boolean {
  const data = getStorageData();
  const index = data.problems.findIndex(p => p.id === id);

  if (index === -1) return false;

  data.problems[index] = {
    ...data.problems[index],
    title,
    description,
    observed_context,
    severity,
    frequency,
    status,
    tags,
    updated_at: new Date().toISOString()
  };

  saveStorageData(data);
  return true;
}

export function deleteProblem(id: number): boolean {
  const data = getStorageData();
  const originalLen = data.problems.length;
  data.problems = data.problems.filter(p => p.id !== id);

  if (data.problems.length < originalLen) {
    // Cascade delete links
    data.links = data.links.filter(l => l.problem_id !== id);
    // Nullify note references
    data.notes = data.notes.map(n =>
      n.problem_id === id ? { ...n, problem_id: null } : n
    );
    saveStorageData(data);
    return true;
  }
  return false;
}

export function getProblemsCountByStatus(): Record<string, number> {
  const data = getStorageData();
  const counts: Record<string, number> = {};
  data.problems.forEach(p => {
    counts[p.status] = (counts[p.status] || 0) + 1;
  });
  return counts;
}

export function getRecentProblems(limit = 5): Problem[] {
  return getAllProblems().slice(0, limit);
}

// =============================================================================
// IDEAS CRUD
// =============================================================================

export function createIdea(
  title: string,
  pitch = '',
  target_user = '',
  value_prop = '',
  differentiation = '',
  assumptions = '',
  risks = '',
  status: Idea['status'] = 'new',
  score: number | null = null,
  tags = ''
): number {
  const data = getStorageData();
  const now = new Date().toISOString();
  const id = getNextId(data, 'ideas');

  const idea: Idea = {
    id,
    title,
    pitch,
    target_user,
    value_prop,
    differentiation,
    assumptions,
    risks,
    status,
    score,
    tags,
    created_at: now,
    updated_at: now
  };

  data.ideas.push(idea);
  saveStorageData(data);
  return id;
}

export function getAllIdeas(): Idea[] {
  const data = getStorageData();
  return [...data.ideas].sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

export function getIdeaById(id: number): Idea | null {
  const data = getStorageData();
  return data.ideas.find(i => i.id === id) || null;
}

export function updateIdea(
  id: number,
  title: string,
  pitch: string,
  target_user: string,
  value_prop: string,
  differentiation: string,
  assumptions: string,
  risks: string,
  status: Idea['status'],
  score: number | null,
  tags: string
): boolean {
  const data = getStorageData();
  const index = data.ideas.findIndex(i => i.id === id);

  if (index === -1) return false;

  data.ideas[index] = {
    ...data.ideas[index],
    title,
    pitch,
    target_user,
    value_prop,
    differentiation,
    assumptions,
    risks,
    status,
    score,
    tags,
    updated_at: new Date().toISOString()
  };

  saveStorageData(data);
  return true;
}

export function deleteIdea(id: number): boolean {
  const data = getStorageData();
  const originalLen = data.ideas.length;
  data.ideas = data.ideas.filter(i => i.id !== id);

  if (data.ideas.length < originalLen) {
    // Cascade delete links
    data.links = data.links.filter(l => l.idea_id !== id);
    // Nullify note references
    data.notes = data.notes.map(n =>
      n.idea_id === id ? { ...n, idea_id: null } : n
    );
    saveStorageData(data);
    return true;
  }
  return false;
}

export function getIdeasCountByStatus(): Record<string, number> {
  const data = getStorageData();
  const counts: Record<string, number> = {};
  data.ideas.forEach(i => {
    counts[i.status] = (counts[i.status] || 0) + 1;
  });
  return counts;
}

export function getRecentIdeas(limit = 5): Idea[] {
  return getAllIdeas().slice(0, limit);
}

// =============================================================================
// PROBLEM-IDEA LINKS
// =============================================================================

export function linkProblemToIdea(problem_id: number, idea_id: number): boolean {
  const data = getStorageData();

  // Check if link already exists
  if (data.links.some(l => l.problem_id === problem_id && l.idea_id === idea_id)) {
    return false;
  }

  const id = getNextId(data, 'links');
  data.links.push({ id, problem_id, idea_id });
  saveStorageData(data);
  return true;
}

export function unlinkProblemFromIdea(problem_id: number, idea_id: number): boolean {
  const data = getStorageData();
  const originalLen = data.links.length;
  data.links = data.links.filter(l =>
    !(l.problem_id === problem_id && l.idea_id === idea_id)
  );

  if (data.links.length < originalLen) {
    saveStorageData(data);
    return true;
  }
  return false;
}

export function getIdeasForProblem(problem_id: number): Idea[] {
  const data = getStorageData();
  const ideaIds = data.links
    .filter(l => l.problem_id === problem_id)
    .map(l => l.idea_id);
  return data.ideas.filter(i => ideaIds.includes(i.id));
}

export function getProblemsForIdea(idea_id: number): Problem[] {
  const data = getStorageData();
  const problemIds = data.links
    .filter(l => l.idea_id === idea_id)
    .map(l => l.problem_id);
  return data.problems.filter(p => problemIds.includes(p.id));
}

export function getLinkedProblemIdsForIdea(idea_id: number): number[] {
  const data = getStorageData();
  return data.links
    .filter(l => l.idea_id === idea_id)
    .map(l => l.problem_id);
}

export function setProblemLinksForIdea(idea_id: number, problem_ids: number[]): void {
  const data = getStorageData();

  // Remove existing links for this idea
  data.links = data.links.filter(l => l.idea_id !== idea_id);

  // Add new links
  problem_ids.forEach(problem_id => {
    const id = getNextId(data, 'links');
    data.links.push({ id, problem_id, idea_id });
  });

  saveStorageData(data);
}

// =============================================================================
// NOTES CRUD
// =============================================================================

export function createNote(
  note_type: Note['note_type'],
  content: string,
  links = '',
  problem_id: number | null = null,
  idea_id: number | null = null
): number {
  const data = getStorageData();
  const now = new Date().toISOString();
  const id = getNextId(data, 'notes');

  const note: Note = {
    id,
    note_type,
    content,
    links,
    problem_id,
    idea_id,
    created_at: now
  };

  data.notes.push(note);
  saveStorageData(data);
  return id;
}

export function getAllNotes(): Note[] {
  const data = getStorageData();
  return [...data.notes].sort((a, b) =>
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
}

export function getNoteById(id: number): Note | null {
  const data = getStorageData();
  return data.notes.find(n => n.id === id) || null;
}

export function updateNote(
  id: number,
  note_type: Note['note_type'],
  content: string,
  links: string,
  problem_id: number | null,
  idea_id: number | null
): boolean {
  const data = getStorageData();
  const index = data.notes.findIndex(n => n.id === id);

  if (index === -1) return false;

  data.notes[index] = {
    ...data.notes[index],
    note_type,
    content,
    links,
    problem_id,
    idea_id
  };

  saveStorageData(data);
  return true;
}

export function deleteNote(id: number): boolean {
  const data = getStorageData();
  const originalLen = data.notes.length;
  data.notes = data.notes.filter(n => n.id !== id);

  if (data.notes.length < originalLen) {
    saveStorageData(data);
    return true;
  }
  return false;
}

export function getNotesForProblem(problem_id: number): Note[] {
  const data = getStorageData();
  return data.notes
    .filter(n => n.problem_id === problem_id)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
}

export function getNotesForIdea(idea_id: number): Note[] {
  const data = getStorageData();
  return data.notes
    .filter(n => n.idea_id === idea_id)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
}

// =============================================================================
// DATA MANAGEMENT
// =============================================================================

export function exportAllData(): StorageData {
  return getStorageData();
}

export function importAllData(data: StorageData): boolean {
  try {
    saveStorageData(data);
    return true;
  } catch {
    return false;
  }
}

export function clearAllData(): void {
  const initial: StorageData = {
    problems: [],
    ideas: [],
    notes: [],
    links: [],
    counters: { problems: 0, ideas: 0, notes: 0, links: 0 }
  };
  saveStorageData(initial);
}
