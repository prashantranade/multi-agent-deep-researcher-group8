'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { History, Eye, Trash2, ArrowRight } from 'lucide-react';
import { HistoryItem } from '@/lib/types';

export default function HistoryLogs() {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    const items = JSON.parse(localStorage.getItem('research_history') || '[]');
    setHistory(items);
  }, []);

  const deleteItem = (id: string) => {
    const updated = history.filter(item => item.id !== id);
    setHistory(updated);
    localStorage.setItem('research_history', JSON.stringify(updated));
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center gap-3 border-b border-slate-800/80 pb-6">
        <History className="w-8 h-8 text-indigo-400" />
        <div>
          <h1 className="text-2xl font-bold text-slate-200">Research Logs History</h1>
          <p className="text-sm text-slate-500">Track and retrieve output documents from your past crew executions.</p>
        </div>
      </div>

      <div className="glass-panel rounded-3xl overflow-hidden">
        {history.length > 0 ? (
          <div className="divide-y divide-slate-800/60">
            {history.map((item) => (
              <div key={item.id} className="p-6 flex items-center justify-between flex-wrap gap-4 hover:bg-slate-900/30 transition-colors">
                <div className="space-y-1">
                  <span className="font-semibold text-slate-200 text-base block">{item.topic}</span>
                  <div className="flex items-center gap-3 text-xs text-slate-500">
                    <span className="capitalize px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800/80 font-medium text-slate-400">{item.persona.replace('_', ' ')}</span>
                    <span>•</span>
                    <span>{item.timestamp}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-md font-semibold ${
                    item.status === 'complete' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                    item.status === 'failed' ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                    'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse'
                  }`}>
                    {item.status}
                  </span>
                  <Link
                    href={`/research/${item.id}`}
                    className="p-2 rounded-lg border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 transition-colors"
                    title="View execution"
                  >
                    <Eye className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => deleteItem(item.id)}
                    className="p-2 rounded-lg border border-slate-800 hover:border-red-900/50 hover:text-red-400 text-slate-500 transition-colors cursor-pointer"
                    title="Delete record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 text-slate-500 space-y-4">
            <p className="text-sm">No research sessions logged yet.</p>
            <Link href="/research" className="inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-400 hover:underline">
              Deploy your first crew <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
