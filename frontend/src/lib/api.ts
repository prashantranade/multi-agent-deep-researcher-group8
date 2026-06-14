import { Source, ResearchBrief, TaskStatusResponse, TaskResultsResponse } from './types';

const API_BASE = 'http://localhost:8000/api';

export async function discoverSources(topic: string): Promise<Source[]> {
  const res = await fetch(`${API_BASE}/sources/discover`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic }),
  });
  if (!res.ok) throw new Error('Failed to discover sources');
  return res.json();
}

export async function startResearch(brief: ResearchBrief): Promise<{ task_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/research/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(brief),
  });
  if (!res.ok) throw new Error('Failed to start research');
  return res.json();
}

export async function getResearchStatus(taskId: string): Promise<TaskStatusResponse> {
  const res = await fetch(`${API_BASE}/research/status/${taskId}`);
  if (res.status === 404) throw new Error('Task not found');
  if (!res.ok) throw new Error('Failed to retrieve task status');
  return res.json();
}

export async function getResearchResults(taskId: string): Promise<TaskResultsResponse> {
  const res = await fetch(`${API_BASE}/research/results/${taskId}`);
  if (res.status === 404) throw new Error('Task not found');
  if (!res.ok) throw new Error('Failed to retrieve task results');
  return res.json();
}

export async function uploadDocument(file: File): Promise<{ text: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/context/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error('Failed to upload and parse document');
  return res.json();
}

