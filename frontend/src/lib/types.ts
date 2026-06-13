export interface Source {
  title: string;
  url: string;
  domain: string;
  date?: string;
  overall_score?: number;
  relevance_score?: number;
  credibility_score?: number;
  trust_score?: number;
}

export interface ResearchBrief {
  topic: string;
  persona: string;
  audience: string;
  tone: string;
  depth: string;
  selected_sources: Source[];
  selected_artifacts: string[];
  context_text?: string;
}

export interface Artifact {
  type: string;
  content: string;
  citations: string[];
}

export interface TaskStatusResponse {
  task_id: string;
  status: 'running' | 'complete' | 'failed';
  notes: string[];
  error: string | null;
}

export interface TaskResultsResponse {
  task_id: string;
  artifacts: Artifact[];
}

export interface HistoryItem {
  id: string;
  topic: string;
  persona: string;
  timestamp: string;
  status: string;
}
