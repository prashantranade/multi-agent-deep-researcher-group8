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
      <div className="flex items-center gap-3 border-b border-slate-200 pb-6">
        <History className="w-8 h-8 text-indigo-600" />
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Research Logs History</h1>
          <p className="text-sm text-slate-500">Track and retrieve output documents from your past crew executions.</p>
        </div>
      </div>

      <div className="clean-card rounded-3xl overflow-hidden">
        {history.length > 0 ? (
          <div className="divide-y divide-slate-100">
            {history.map((item) => (
              <div key={item.id} className="p-6 flex items-center justify-between flex-wrap gap-4 hover:bg-slate-50/50 transition-colors">
                <div className="space-y-1.5">
                  <span className="font-bold text-slate-800 text-base block leading-snug">{item.topic}</span>
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span className="capitalize px-2 py-0.5 rounded bg-slate-50 border border-slate-200 font-semibold text-slate-600">{item.persona.replace('_', ' ')}</span>
                    <span>•</span>
                    <span>{item.timestamp}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2.5 py-1 rounded-md font-bold border ${
                    item.status === 'complete' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                    item.status === 'failed' ? 'bg-red-50 text-red-700 border-red-200' :
                    'bg-indigo-50 text-indigo-700 border-indigo-200 animate-pulse'
                  }`}>
                    {item.status}
                  </span>
                  <Link
                    href={`/research/${item.id}`}
                    className="p-2 rounded-lg border border-slate-200 hover:border-slate-350 hover:bg-slate-50 text-slate-500 hover:text-slate-800 transition-all"
                    title="View execution"
                  >
                    <Eye className="w-4 h-4" />
                  </Link>
                  <button
                    onClick={() => deleteItem(item.id)}
                    className="p-2 rounded-lg border border-slate-200 hover:border-red-200 hover:bg-red-50 hover:text-red-600 text-slate-400 transition-all cursor-pointer"
                    title="Delete record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20 text-slate-450 space-y-4">
            <p className="text-sm">No research sessions logged yet.</p>
            <Link href="/research" className="inline-flex items-center gap-1.5 text-sm font-bold text-indigo-650 hover:underline">
              Deploy your first crew <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
