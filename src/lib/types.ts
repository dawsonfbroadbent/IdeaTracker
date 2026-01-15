export interface Problem {
  id: number;
  title: string;
  description: string;
  observed_context: string;
  severity: number;
  frequency: 'rare' | 'weekly' | 'daily';
  status: 'open' | 'solved' | 'ignored';
  tags: string;
  created_at: string;
  updated_at: string;
}

export interface Idea {
  id: number;
  title: string;
  pitch: string;
  target_user: string;
  value_prop: string;
  differentiation: string;
  assumptions: string;
  risks: string;
  status: 'new' | 'researching' | 'validating' | 'building' | 'parked';
  score: number | null;
  tags: string;
  created_at: string;
  updated_at: string;
}

export interface Note {
  id: number;
  note_type: 'interview' | 'competitor' | 'pricing' | 'tech' | 'general';
  content: string;
  links: string;
  problem_id: number | null;
  idea_id: number | null;
  created_at: string;
}

export interface ProblemIdeaLink {
  id: number;
  problem_id: number;
  idea_id: number;
}

export interface StorageData {
  problems: Problem[];
  ideas: Idea[];
  notes: Note[];
  links: ProblemIdeaLink[];
  counters: {
    problems: number;
    ideas: number;
    notes: number;
    links: number;
  };
}
