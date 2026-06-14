'use client';

import { useEffect, useState, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { getResearchStatus, getResearchResults } from '@/lib/api';
import { Artifact, TaskStatusResponse } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import { Loader2, CheckCircle2, XCircle, Terminal, ClipboardCheck, Clipboard, Download, ArrowLeft, FileText, Calendar, User, AlignLeft } from 'lucide-react';

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
  const [error, setError] = useState<string | null>(null);

  const logEndRef = useRef<HTMLDivElement>(null);

  // Fetch status
  const pollStatus = async () => {
    try {
      const data = await getResearchStatus(task_id);
      setStatusData(data);
      setPollingErrorCount(0);
      setError(null);

      if (data.status === 'complete') {
        fetchResults();
        return true; // Stop polling
      }
      if (data.status === 'failed') {
        return true; // Stop polling
      }
    } catch (err: any) {
      if (err.message === 'Task not found') {
        setError('Task not found. The backend server might have restarted, clearing the task from in-memory storage.');
        return true; // Stop polling
      }
      setPollingErrorCount(c => c + 1);
      if (pollingErrorCount > 10) {
        setError('Failed to connect to the backend server. Please verify it is running.');
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
  const topic = runInfo?.topic || 'General Agentic Research Topic';
  // @ts-ignore
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
    <div className="space-y-10 max-w-4xl mx-auto">
      {/* Navigation / Header */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-6">
        <button
          onClick={() => router.push('/research')}
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Research
        </button>
        
        <div className="text-right">
          <span className="text-xs text-slate-400 uppercase tracking-widest block mb-1">TASK ID</span>
          <span className="font-mono text-xs text-slate-800 font-bold bg-white border border-slate-200 px-3 py-1 rounded-md">{task_id}</span>
        </div>
      </div>

      {error && (
        <div className="p-8 rounded-3xl bg-slate-50 border border-slate-200 text-center flex flex-col items-center max-w-md mx-auto">
          <XCircle className="w-12 h-12 text-slate-400 mb-4" />
          <h3 className="text-xl font-bold text-slate-800 mb-2">Research Task Error</h3>
          <p className="text-sm text-slate-500 mb-6">{error}</p>
          <button
            onClick={() => router.push('/research')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm transition-colors cursor-pointer shadow-sm hover:shadow"
          >
            Start New Research
          </button>
        </div>
      )}

      {/* Polling / Status Display */}
      {statusData && statusData.status !== 'complete' && statusData.status !== 'failed' && (
        <div className="clean-card rounded-3xl p-8 text-center flex flex-col items-center">
          <Loader2 className="w-10 h-10 text-indigo-600 animate-spin mb-4" />
          <h3 className="text-xl font-bold text-slate-800 mb-2">Agents Executing Workflow...</h3>
          <p className="text-sm text-slate-500 max-w-md">Your strategic deep researcher crew is processing search queries and synthesizing knowledge.</p>
        </div>
      )}

      {statusData && statusData.status === 'failed' && (
        <div className="p-8 rounded-3xl bg-red-50 border border-red-200 text-center flex flex-col items-center">
          <XCircle className="w-12 h-12 text-red-500 mb-4" />
          <h3 className="text-xl font-bold text-red-800 mb-2">Research Operation Failed</h3>
          <p className="text-sm text-red-600 max-w-md mb-4">{statusData.error || 'Unknown workflow error encountered.'}</p>
          <button
            onClick={() => router.push('/research')}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-red-650 hover:bg-red-750 text-white font-medium text-sm transition-colors cursor-pointer"
          >
            Start New Research
          </button>
        </div>
      )}

      {/* Horizontal Node graph pipeline tracker */}
      {statusData && statusData.status !== 'failed' && (
        <div className="clean-card rounded-3xl p-6">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-6">Workflow Graph Pipeline</span>
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 md:gap-2">
            {pipelineNodes.map((node: string, index: number) => {
              const isActive = activeNode === node;
              const isPast = statusData.status === 'complete' || 
                (pipelineNodes.indexOf(activeNode) > index);
              
              return (
                <div key={node} className="flex flex-1 items-center gap-4 md:gap-2">
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center border text-xs font-bold transition-all duration-300 ${
                      isActive ? 'bg-indigo-600 border-indigo-600 text-white animate-pulse shadow-md shadow-indigo-100' :
                      isPast ? 'bg-emerald-50 border-emerald-500 text-emerald-700' :
                      'bg-slate-50 border-slate-200 text-slate-400'
                    }`}>
                      {isPast ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : index + 1}
                    </div>
                    <span className={`text-sm font-semibold capitalize ${
                      isActive ? 'text-indigo-600 font-bold' :
                      isPast ? 'text-slate-800' :
                      'text-slate-400'
                    }`}>
                      {node.replace('_', ' ')}
                    </span>
                  </div>
                  {index < pipelineNodes.length - 1 && (
                    <div className="hidden md:block flex-1 h-px bg-slate-200 mx-2" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Research Footprints Timeline Audit Trail */}
      {statusData && statusData.status !== 'failed' && statusData.notes && statusData.notes.length > 0 && (
        <div className="clean-card rounded-3xl p-8 space-y-6">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Research Footprints</h3>
          <div className="relative border-l border-slate-200 ml-4 pl-6 space-y-6">
            {statusData.notes.map((note: string, i: number) => {
              const isLast = i === statusData.notes.length - 1;
              return (
                <div key={i} className="relative">
                  {/* Timeline circle dot */}
                  <div className={`absolute -left-[31px] top-0.5 w-4.5 h-4.5 rounded-full border flex items-center justify-center ${
                    isLast && statusData.status === 'running'
                      ? 'bg-indigo-600 border-indigo-600 text-white animate-pulse'
                      : 'bg-emerald-500 border-emerald-500 text-white'
                  }`}>
                    {isLast && statusData.status === 'running' ? (
                      <Loader2 className="w-2.5 h-2.5 animate-spin" />
                    ) : (
                      <div className="w-1.5 h-1.5 rounded-full bg-white" />
                    )}
                  </div>
                  <div>
                    <p className={`text-sm font-medium ${isLast ? 'text-slate-800 font-bold' : 'text-slate-600'}`}>
                      {note}
                    </p>
                    <span className="text-[10px] text-slate-400 block mt-0.5">{new Date().toLocaleTimeString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Toggleable Technical logs drawer */}
      {statusData && statusData.status !== 'failed' && statusData.notes && statusData.notes.length > 0 && (
        <details className="group">
          <summary className="text-xs font-bold text-slate-500 hover:text-slate-700 cursor-pointer list-none flex items-center gap-1.5 p-2 w-fit rounded-lg hover:bg-slate-100 transition-colors">
            <Terminal className="w-3.5 h-3.5 text-slate-500" />
            <span>Show Technical Agent Logs</span>
            <span className="transition-transform group-open:rotate-90">➔</span>
          </summary>
          
          <div className="mt-3 rounded-2xl overflow-hidden border border-slate-800">
            <div className="px-5 py-3 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Raw Monospace Logs</span>
              <span className="text-[10px] text-slate-500 font-mono">PAGER=cat</span>
            </div>
            <div className="p-6 bg-slate-950 font-mono text-xs text-slate-300 space-y-2 h-[200px] overflow-y-auto">
              {statusData.notes.map((note: string, i: number) => (
                <div key={i} className="leading-relaxed flex gap-2">
                  <span className="text-slate-700 select-none">[{new Date().toLocaleTimeString()}]</span>
                  <span>{note}</span>
                </div>
              ))}
              {statusData.status === 'running' && (
                <div className="flex items-center gap-2 text-indigo-400 animate-pulse">
                  <span>➔</span> <span>Waiting for node transitions...</span>
                </div>
              )}
              <div ref={logEndRef} />
            </div>
          </div>
        </details>
      )}

      {/* Complete Artifacts Display in White Paper format */}
      {statusData?.status === 'complete' && artifacts.length > 0 && (
        <div className="space-y-12">
          <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
            <FileText className="w-6 h-6 text-indigo-600" /> Constructed Research Artifacts ({artifacts.length})
          </h2>

          <div className="space-y-12">
            {artifacts.map((art, idx) => (
              <div key={idx} className="paper-sheet rounded-3xl overflow-hidden shadow-md border border-slate-200">
                
                {/* Document Metadata Header block */}
                <div className="p-10 md:p-14 pb-4 border-b border-slate-100 bg-slate-50/50">
                  <div className="flex justify-between items-start flex-wrap gap-4 mb-8">
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest block">Deep Researcher Document</span>
                      <h1 className="text-3xl font-black text-slate-900 tracking-tight capitalize">{art.type.replace('_', ' ')}</h1>
                    </div>
                    
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleCopy(art.content, idx)}
                        className="p-2 rounded-lg border border-slate-200 hover:border-slate-300 text-slate-500 hover:text-slate-800 hover:bg-white transition-all cursor-pointer"
                        title="Copy text to clipboard"
                      >
                        {copiedIndex === idx ? <ClipboardCheck className="w-4 h-4 text-emerald-600" /> : <Clipboard className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => handleDownload(art)}
                        className="p-2 rounded-lg border border-slate-200 hover:border-slate-300 text-slate-500 hover:text-slate-800 hover:bg-white transition-all cursor-pointer"
                        title="Download Markdown file"
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Document Metadata list */}
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-6 text-xs text-slate-500 pt-2 font-sans">
                    <div className="flex items-center gap-2">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      <div>
                        <span className="text-slate-400 block uppercase tracking-wider text-[9px] font-bold">Persona Crew</span>
                        <span className="font-semibold text-slate-700 capitalize">{persona.replace('_', ' ')}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <AlignLeft className="w-3.5 h-3.5 text-slate-400" />
                      <div>
                        <span className="text-slate-400 block uppercase tracking-wider text-[9px] font-bold">Research Topic</span>
                        <span className="font-semibold text-slate-700 truncate block max-w-[200px]">{topic}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      <div>
                        <span className="text-slate-400 block uppercase tracking-wider text-[9px] font-bold">Generated On</span>
                        <span className="font-semibold text-slate-700">{new Date().toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Formatted Markdown document body */}
                <div className="p-10 md:p-14 pt-8 doc-prose">
                  <ReactMarkdown>{art.content}</ReactMarkdown>
                </div>

                {/* Citations section if any exist */}
                {art.citations && art.citations.length > 0 && (
                  <div className="px-10 md:px-14 py-8 border-t border-slate-100 bg-slate-50/30">
                    <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 font-sans select-none">
                      References & Cited Bibliography
                    </h3>
                    <ol className="space-y-3 font-sans text-xs text-slate-600 list-decimal pl-5">
                      {art.citations.map((cite, i) => (
                        <li key={i} className="leading-relaxed">
                          <a 
                            href={cite} 
                            target="_blank" 
                            rel="noopener noreferrer" 
                            className="text-indigo-650 hover:underline break-all font-medium"
                          >
                            {cite}
                          </a>
                        </li>
                      ))}
                    </ol>
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
