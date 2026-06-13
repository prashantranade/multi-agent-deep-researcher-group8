'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getResearchStatus, getResearchResults } from '@/lib/api';
import { Artifact, TaskStatusResponse } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import { Loader2, CheckCircle2, XCircle, Terminal, ClipboardCheck, Clipboard, Download, ArrowLeft, RefreshCw, FileText } from 'lucide-react';

// Node graphs configurations
const PERSONA_PIPELINES = {
  bharat_desha: ['trend', 'seo', 'retrieve', 'analyse', 'generate_artifacts'],
  product_manager: ['retrieve', 'analyse', 'generate_artifacts'],
  content_creator: ['retrieve', 'analyse', 'generate_artifacts']
};

export default function LiveTracker() {
  const { task_id } = useParams<{ task_id: string }>();
  const router = useRouter();
  const [statusData, setStatusData] = useState<TaskStatusResponse | null>(null);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [pollingErrorCount, setPollingErrorCount] = useState(0);

  const logEndRef = useRef<HTMLDivElement>(null);

  // Fetch status
  const pollStatus = async () => {
    try {
      const data = await getResearchStatus(task_id);
      setStatusData(data);
      setPollingErrorCount(0);

      if (data.status === 'complete') {
        fetchResults();
        return true; // Stop polling
      }
      if (data.status === 'failed') {
        return true; // Stop polling
      }
    } catch (err) {
      setPollingErrorCount(c => c + 1);
      if (pollingErrorCount > 10) {
        return true; // Stop polling after 10 failures
      }
    }
    return false;
  };

  const fetchResults = async () => {
    try {
      const results = await getResearchResults(task_id);
      setArtifacts(results.artifacts);

      // Update status in localStorage history
      const savedHistory = JSON.parse(localStorage.getItem('research_history') || '[]');
      const updated = savedHistory.map((item: any) => 
        item.id === task_id ? { ...item, status: 'complete' } : item
      );
      localStorage.setItem('research_history', JSON.stringify(updated));
    } catch (err) {
      console.error('Error fetching results:', err);
    }
  };

  useEffect(() => {
    // Start immediately
    pollStatus();

    const interval = setInterval(async () => {
      const shouldStop = await pollStatus();
      if (shouldStop) {
        clearInterval(interval);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [task_id]);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [statusData?.notes]);

  const handleCopy = (content: string, index: number) => {
    navigator.clipboard.writeText(content);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleDownload = (artifact: Artifact) => {
    const blob = new Blob([artifact.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.type}_research_report.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Determine executing persona to fetch pipeline nodes
  const savedHistory = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('research_history') || '[]') : [];
  const runInfo = savedHistory.find((item: any) => item.id === task_id);
  const persona = runInfo?.persona || 'product_manager';
  const pipelineNodes = PERSONA_PIPELINES[persona as keyof typeof PERSONA_PIPELINES] || PERSONA_PIPELINES.product_manager;

  // Estimate active node based on status & log size
  const getActiveNode = () => {
    if (!statusData) return '';
    if (statusData.status === 'complete') return '';
    if (statusData.status === 'failed') return '';
    
    const notes = statusData.notes || [];
    const noteCount = notes.length;

    if (persona === 'bharat_desha') {
      if (noteCount <= 1) return 'trend';
      if (noteCount === 2) return 'seo';
      if (noteCount === 3) return 'retrieve';
      if (noteCount === 4) return 'analyse';
      return 'generate_artifacts';
    } else {
      if (noteCount <= 1) return 'retrieve';
      if (noteCount === 2) return 'analyse';
      return 'generate_artifacts';
    }
  };

  const activeNode = getActiveNode();

  return (
    <div className="space-y-10 max-w-5xl mx-auto">
      {/* Navigation / Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-6">
        <button
          onClick={() => router.push('/research')}
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Research
        </button>
        
        <div className="text-right">
          <span className="text-xs text-slate-500 uppercase tracking-widest block mb-1">TASK ID</span>
          <span className="font-mono text-sm text-slate-300 font-bold bg-slate-900 border border-slate-800/80 px-3 py-1 rounded-md">{task_id}</span>
        </div>
      </div>

      {/* Polling / Status Display */}
      {statusData && statusData.status !== 'complete' && statusData.status !== 'failed' && (
        <div className="glass-panel rounded-3xl p-8 text-center flex flex-col items-center">
          <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mb-4" />
          <h3 className="text-xl font-bold text-slate-200 mb-2">Agents Hard at Work...</h3>
          <p className="text-sm text-slate-400 max-w-md">The Deep Researcher crew is executing state graph transitions in background threads. Watch progress below.</p>
        </div>
      )}

      {statusData && statusData.status === 'failed' && (
        <div className="p-8 rounded-3xl bg-red-950/20 border border-red-900/50 text-center flex flex-col items-center">
          <XCircle className="w-12 h-12 text-red-500 mb-4" />
          <h3 className="text-xl font-bold text-red-200 mb-2">Research Operation Failed</h3>
          <p className="text-sm text-red-400 max-w-md mb-4">{statusData.error || 'Unknown workflow error encountered.'}</p>
          <button
            onClick={() => router.push('/research')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-900/50 hover:bg-red-900/80 text-white font-medium text-sm transition-colors cursor-pointer"
          >
            Start New Research
          </button>
        </div>
      )}

      {/* Horizontal Node graph pipeline tracker */}
      {statusData && statusData.status !== 'failed' && (
        <div className="glass-panel rounded-3xl p-6">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider block mb-6">Workflow Graph Pipeline</span>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 md:gap-2">
            {pipelineNodes.map((node: string, index: number) => {
              const isActive = activeNode === node;
              const isPast = statusData.status === 'complete' || 
                (pipelineNodes.indexOf(activeNode) > index);
              
              return (
                <div key={node} className="flex flex-1 items-center gap-4 md:gap-2">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 ${
                      isActive ? 'bg-indigo-500 border-indigo-400 text-white animate-pulse live-glow' :
                      isPast ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' :
                      'bg-slate-900 border-slate-800 text-slate-600'
                    }`}>
                      {isPast ? <CheckCircle2 className="w-5 h-5" /> : index + 1}
                    </div>
                    <span className={`text-sm font-semibold capitalize ${
                      isActive ? 'text-indigo-400 font-bold' :
                      isPast ? 'text-slate-300' :
                      'text-slate-500'
                    }`}>
                      {node.replace('_', ' ')}
                    </span>
                  </div>
                  {index < pipelineNodes.length - 1 && (
                    <div className="hidden md:block flex-1 h-px bg-slate-800 mx-2" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Scrollable monospace live console logs */}
      {statusData && statusData.status !== 'failed' && (
        <div className="glass-panel rounded-3xl overflow-hidden border border-slate-800/80">
          <div className="px-5 py-3.5 bg-slate-900/80 border-b border-slate-800/80 flex items-center gap-2">
            <Terminal className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Live Agent Exec Logs</span>
          </div>
          <div className="p-6 bg-slate-955 font-mono text-xs text-purple-400 space-y-3 h-[250px] overflow-y-auto">
            {statusData.notes && statusData.notes.map((note: string, i: number) => (
              <div key={i} className="leading-relaxed flex gap-2">
                <span className="text-slate-700 select-none">[{new Date().toLocaleTimeString()}]</span>
                <span className="text-purple-300">{note}</span>
              </div>
            ))}
            {statusData.status === 'running' && (
              <div className="flex items-center gap-2 text-indigo-400 animate-pulse">
                <span>➔</span> <span>Waiting for next node transition...</span>
              </div>
            )}
            {statusData.status === 'complete' && (
              <div className="text-emerald-400 font-bold">
                ✓ Core execution workflow finished successfully. Compile outputs below.
              </div>
            )}
            {(!statusData.notes || statusData.notes.length === 0) && (
              <div className="text-slate-600 italic">Initializing researcher subprocess...</div>
            )}
            <div ref={logEndRef} />
          </div>
        </div>
      )}

      {/* Complete Artifacts Display */}
      {statusData?.status === 'complete' && artifacts.length > 0 && (
        <div className="space-y-8">
          <h2 className="text-2xl font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-6 h-6 text-indigo-400" /> Constructed Artifacts ({artifacts.length})
          </h2>

          <div className="space-y-8">
            {artifacts.map((art, idx) => (
              <div key={idx} className="glass-panel rounded-3xl overflow-hidden shadow-xl border border-slate-800/80">
                {/* Artifact Title header bar */}
                <div className="px-6 py-4.5 bg-slate-900/60 border-b border-slate-800/80 flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center gap-2.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                    <span className="font-bold text-slate-100 capitalize">{art.type.replace('_', ' ')}</span>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleCopy(art.content, idx)}
                      className="p-2 rounded-lg border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                      title="Copy to clipboard"
                    >
                      {copiedIndex === idx ? <ClipboardCheck className="w-4 h-4 text-emerald-400" /> : <Clipboard className="w-4 h-4" />}
                    </button>
                    <button
                      onClick={() => handleDownload(art)}
                      className="p-2 rounded-lg border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                      title="Download Markdown file"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Artifact markdown rendering body */}
                <div className="p-8 prose prose-invert prose-indigo max-w-none prose-p:text-slate-300 prose-p:leading-relaxed prose-headings:text-slate-100 prose-headings:font-bold">
                  <ReactMarkdown>{art.content}</ReactMarkdown>
                </div>

                {/* Citations section if any exist */}
                {art.citations && art.citations.length > 0 && (
                  <div className="px-8 py-5 border-t border-slate-800/60 bg-slate-900/20">
                    <details className="group">
                      <summary className="text-xs font-bold text-slate-400 hover:text-slate-300 cursor-pointer list-none flex items-center gap-2">
                        <span className="transition-transform group-open:rotate-90">➔</span>
                        Citations & Sources ({art.citations.length})
                      </summary>
                      <ul className="mt-4 space-y-2.5 pl-4 border-l border-slate-800">
                        {art.citations.map((cite, i) => (
                          <li key={i} className="text-xs text-slate-400">
                            <a href={cite} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline break-all">{cite}</a>
                          </li>
                        ))}
                      </ul>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
