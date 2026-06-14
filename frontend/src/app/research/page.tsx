'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { discoverSources, startResearch, uploadDocument } from '@/lib/api';
import { Source } from '@/lib/types';
import { Sparkles, Globe, User, Settings, CheckSquare, FileText, ChevronRight, ChevronLeft, Loader2, ArrowRight } from 'lucide-react';

const PERSONAS = [
  { id: 'product_manager', name: 'Product Manager', desc: 'Focuses on PRD insights, opportunities, and competitive landscapes.' },
  { id: 'content_creator', name: 'Content Creator', desc: 'Focuses on social copy, hashtags, content briefs, and calendars.' },
  { id: 'bharat_desha', name: 'Bharat Desha', desc: 'Indian regional travel, SEO, itineraries, guides, and culture.' }
];

const TONES = {
  product_manager: ['Professional', 'Technical', 'Direct', 'Visionary'],
  content_creator: ['Professional', 'Casual', 'Informative', 'Witty', 'Empathetic'],
  bharat_desha: ['Inspirational', 'Informative', 'Cultural', 'Warm']
};

const AUDIENCES = {
  product_manager: ['Developers', 'Executives', 'End Users', 'Internal Stakeholders'],
  content_creator: ['General', 'SaaS Founders', 'Marketers', 'Tech Enthusiasts'],
  bharat_desha: ['Tourists', 'Pilgrims', 'Adventure Seekers', 'Families']
};

const ARTIFACT_OPTIONS = {
  product_manager: [
    { id: 'research_brief', label: 'Research Brief' },
    { id: 'competitive_summary', label: 'Competitive Summary' },
    { id: 'opportunity_sizing', label: 'Opportunity Sizing Matrix' },
    { id: 'prd_insights', label: 'PRD Insights Report' }
  ],
  content_creator: [
    { id: 'content_brief', label: 'Content Brief' },
    { id: 'social_draft', label: 'Social Draft Copy' },
    { id: 'captions', label: 'Image/Video Captions' },
    { id: 'hashtags', label: 'Hashtag Set' },
    { id: 'calendar_entry', label: 'Social Calendar Schedule' }
  ],
  bharat_desha: [
    { id: 'blog_post', label: 'Blog Post' },
    { id: 'itinerary', label: 'Travel Itinerary' },
    { id: 'destination_guide', label: 'Destination Guide Book' },
    { id: 'wellness_guide', label: 'Wellness/Cultural Guide' },
    { id: 'instagram', label: 'Instagram Copy' },
    { id: 'facebook', label: 'Facebook Copy' },
    { id: 'x_post', label: 'X (Twitter) Draft' },
    { id: 'youtube', label: 'YouTube Script Outline' }
  ]
};

export default function ResearchWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  
  // Wizard States
  const [persona, setPersona] = useState('product_manager');
  const [topic, setTopic] = useState('');
  const [sources, setSources] = useState<Source[]>([]);
  const [selectedSources, setSelectedSources] = useState<Source[]>([]);
  const [audience, setAudience] = useState('General');
  const [tone, setTone] = useState('Professional');
  const [depth, setDepth] = useState('standard');
  const [selectedArtifacts, setSelectedArtifacts] = useState<string[]>([]);
  const [contextText, setContextText] = useState('');
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [parsingDocument, setParsingDocument] = useState(false);

  const [loadingSources, setLoadingSources] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Helpers
  const handleDiscoverSources = async () => {
    if (!topic.trim()) return;
    setLoadingSources(true);
    try {
      const discovered = await discoverSources(topic);
      setSources(discovered);
      setSelectedSources(discovered); // Check all by default
      setStep(3);
    } catch (err) {
      alert('Error discovering sources. Please check backend connection.');
    } finally {
      setLoadingSources(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploadedFileName(file.name);
    const filename = file.name.toLowerCase();
    
    if (filename.endsWith('.pdf') || filename.endsWith('.docx')) {
      setParsingDocument(true);
      try {
        const res = await uploadDocument(file);
        setContextText(res.text);
      } catch (err) {
        alert('Failed to parse document. Ensure the backend API server is running.');
        setUploadedFileName('');
      } finally {
        setParsingDocument(false);
      }
    } else {
      // client-side reader for txt, md, json, csv
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        if (file.name.endsWith('.json')) {
          try {
            const parsed = JSON.parse(text);
            setContextText(JSON.stringify(parsed, null, 2));
          } catch {
            setContextText(text);
          }
        } else {
          setContextText(text);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleArtifactToggle = (id: string) => {
    if (selectedArtifacts.includes(id)) {
      setSelectedArtifacts(selectedArtifacts.filter(a => a !== id));
    } else {
      setSelectedArtifacts([...selectedArtifacts, id]);
    }
  };

  const handleLaunch = async () => {
    if (selectedArtifacts.length === 0) {
      alert('Please select at least one artifact type to generate.');
      return;
    }
    setSubmitting(true);
    try {
      const payload = {
        topic,
        persona,
        audience,
        tone,
        depth,
        selected_sources: selectedSources,
        selected_artifacts: selectedArtifacts,
        context_text: contextText || undefined
      };
      const result = await startResearch(payload);
      
      // Save execution details to history localStorage
      const newRun = {
        id: result.task_id,
        topic,
        persona,
        timestamp: new Date().toLocaleString(),
        status: 'running'
      };
      const savedHistory = JSON.parse(localStorage.getItem('research_history') || '[]');
      localStorage.setItem('research_history', JSON.stringify([newRun, ...savedHistory]));

      // Route to live execution screen
      router.push(`/research/${result.task_id}`);
    } catch (err) {
      alert('Failed to deploy researcher.');
      setSubmitting(false);
    }
  };

  // Auto-update tone/audience recommendation when persona changes
  const selectPersona = (pId: string) => {
    setPersona(pId);
    // @ts-ignore
    setAudience(AUDIENCES[pId]?.[0] || 'General');
    // @ts-ignore
    setTone(TONES[pId]?.[0] || 'Professional');
    setSelectedArtifacts([]);
  };

  return (
    <div className="max-w-3xl mx-auto mt-6">
      {/* Step Indicator Header (7 Steps) */}
      <div className="flex items-center justify-between mb-12 border-b border-slate-200 pb-6">
        {[1, 2, 3, 4, 5, 6, 7].map((s) => (
          <div key={s} className="flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
              step === s ? 'bg-indigo-600 text-white ring-4 ring-indigo-100' :
              step > s ? 'bg-indigo-50 text-indigo-700 border border-indigo-100' :
              'bg-slate-105 border border-slate-200 text-slate-400'
            }`}>
              {s}
            </div>
            <span className={`text-xs font-bold hidden md:inline ${step === s ? 'text-slate-800' : 'text-slate-400'}`}>
              {s === 1 && 'Persona'}
              {s === 2 && 'Topic'}
              {s === 3 && 'Sources'}
              {s === 4 && 'Context Docs'}
              {s === 5 && 'Parameters'}
              {s === 6 && 'Artifacts'}
              {s === 7 && 'Review'}
            </span>
            {s < 7 && <div className="w-3 sm:w-8 h-px bg-slate-200" />}
          </div>
        ))}
      </div>

      {/* Wizard Card Body */}
      <div className="clean-card rounded-3xl p-8 mb-6 relative overflow-hidden">
        
        {/* STEP 1: Persona */}
        {step === 1 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <User className="w-5 h-5 text-indigo-600" /> Choose Persona Crew
            </h2>
            <p className="text-sm text-slate-500 mb-8">Select the strategic perspective that will analyze your research topic.</p>
            
            <div className="grid gap-4">
              {PERSONAS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => selectPersona(p.id)}
                  className={`text-left p-6 rounded-2xl transition-all duration-200 border cursor-pointer ${
                    persona === p.id 
                      ? 'bg-indigo-50/40 border-indigo-500 shadow-sm' 
                      : 'bg-white border-slate-200 hover:border-slate-350'
                  }`}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-bold text-lg text-slate-900">{p.name}</span>
                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                      persona === p.id ? 'border-indigo-600 bg-indigo-600' : 'border-slate-300'
                    }`}>
                      {persona === p.id && <div className="w-2 h-2 rounded-full bg-white" />}
                    </div>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">{p.desc}</p>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 2: Topic input */}
        {step === 2 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Globe className="w-5 h-5 text-indigo-600" /> Enter Research Topic
            </h2>
            <p className="text-sm text-slate-500 mb-8">Specify the core search query. Deep Researcher will fetch web resources to build local memory.</p>
            
            <div className="space-y-6">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Research Topic</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. Sustainable ecotourism projects in Rajasthan or GenAI trends in sales enablement"
                  className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3.5 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
                />
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/60">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">Suggested topics:</span>
                <div className="flex flex-col gap-2.5 text-sm text-slate-600">
                  <button onClick={() => setTopic("Jaipur cultural tourism itineraries")} className="text-left hover:text-indigo-600 transition-colors font-medium">➔ Jaipur cultural tourism itineraries</button>
                  <button onClick={() => setTopic("Comparison of LLM evaluation frameworks")} className="text-left hover:text-indigo-600 transition-colors font-medium">➔ Comparison of LLM evaluation frameworks</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Curate Sources */}
        {step === 3 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Globe className="w-5 h-5 text-indigo-600" /> Curate Discoverable Sources
            </h2>
            <p className="text-sm text-slate-500 mb-8">Verify and curate the list of confidence-scored web resources that our agents will digest.</p>
            
            <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
              {sources.map((s, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-white border border-slate-200 flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={selectedSources.some(x => x.url === s.url)}
                      onChange={() => {
                        if (selectedSources.some(x => x.url === s.url)) {
                          setSelectedSources(selectedSources.filter(x => x.url !== s.url));
                        } else {
                          setSelectedSources([...selectedSources, s]);
                        }
                      }}
                      className="mt-1 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
                    />
                    <div>
                      <span className="font-bold text-slate-800 text-sm block leading-snug mb-1">{s.title}</span>
                      <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-600 hover:underline block mb-1 truncate max-w-[450px]">{s.url}</a>
                      {s.date && <span className="text-xs text-slate-400">{s.date}</span>}
                    </div>
                  </div>
                  {s.overall_score !== undefined && (
                    <span className="text-xs font-bold px-2 py-1 rounded-md bg-indigo-50 border border-indigo-100 text-indigo-700">
                      Score: {Math.round(s.overall_score * 100)}
                    </span>
                  )}
                </div>
              ))}
              {sources.length === 0 && (
                <div className="text-center py-10 text-slate-400 text-sm">No sources discovered. Continue to use default web search backup.</div>
              )}
            </div>
          </div>
        )}

        {/* STEP 4: Context & Document Upload */}
        {step === 4 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-600" /> Upload Documents & Context
            </h2>
            <p className="text-sm text-slate-500 mb-8">Include local text files, markdown documentation, transcripts, or notes to help the agentic crew with custom context.</p>
            
            <div className="space-y-6">
              {/* File upload drag-and-drop zone */}
              <div className="border-2 border-dashed border-slate-200 hover:border-indigo-500 rounded-2xl p-8 text-center transition-colors bg-slate-50/50">
                <input
                  type="file"
                  id="file-upload"
                  onChange={handleFileUpload}
                  accept=".txt,.md,.json,.csv,.pdf,.docx"
                  disabled={parsingDocument}
                  className="hidden"
                />
                <label htmlFor="file-upload" className={`space-y-3 block ${parsingDocument ? 'pointer-events-none' : 'cursor-pointer'}`}>
                  {parsingDocument ? (
                    <div className="flex flex-col items-center justify-center space-y-3 py-2">
                      <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                      <div className="text-sm font-bold text-slate-800 animate-pulse">Extracting text context...</div>
                      <div className="text-xs text-slate-400">Processing {uploadedFileName}</div>
                    </div>
                  ) : (
                    <>
                      <div className="p-3 bg-white w-fit rounded-xl border border-slate-150 mx-auto shadow-sm">
                        <ArrowRight className="w-5 h-5 text-indigo-600 rotate-90" />
                      </div>
                      <div className="text-sm font-bold text-slate-800">
                        {uploadedFileName ? `Selected: ${uploadedFileName}` : 'Select context document file'}
                      </div>
                      <div className="text-xs text-slate-400">Supports TXT, MD, JSON, CSV, PDF, or DOCX (Max 5MB)</div>
                    </>
                  )}
                </label>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Custom Context Notes</label>
                <textarea
                  rows={5}
                  value={contextText}
                  disabled={parsingDocument}
                  onChange={(e) => setContextText(e.target.value)}
                  placeholder={parsingDocument ? "Extracting text context..." : "Paste context contents here, or upload a document above..."}
                  className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-800 placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors resize-none text-sm font-mono leading-relaxed disabled:opacity-50"
                />
              </div>
            </div>
          </div>
        )}

        {/* STEP 5: Configuration Parameters */}
        {step === 5 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Settings className="w-5 h-5 text-indigo-600" /> Setup Configuration
            </h2>
            <p className="text-sm text-slate-500 mb-8">Adjust parameters like target audience segment, communication tone, and depth of analysis.</p>
            
            <div className="grid sm:grid-cols-2 gap-6">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Audience Segment</label>
                <select
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:outline-none focus:border-indigo-500 transition-colors"
                >
                  {/* @ts-ignore */}
                  {AUDIENCES[persona]?.map((a) => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Communication Tone</label>
                <select
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                  className="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-slate-800 focus:outline-none focus:border-indigo-500 transition-colors"
                >
                  {/* @ts-ignore */}
                  {TONES[persona]?.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-3">Research Depth</label>
                <div className="grid grid-cols-3 gap-3">
                  {['quick', 'standard', 'deep'].map((d) => (
                    <button
                      key={d}
                      onClick={() => setDepth(d)}
                      className={`py-3 rounded-xl border text-sm font-semibold capitalize transition-all cursor-pointer ${
                        depth === d
                          ? 'bg-indigo-50 border-indigo-600 text-indigo-700 font-bold'
                          : 'bg-white border-slate-250 text-slate-500 hover:border-slate-350'
                      }`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 6: Selected Artifacts */}
        {step === 6 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <CheckSquare className="w-5 h-5 text-indigo-600" /> Target Artifacts
            </h2>
            <p className="text-sm text-slate-500 mb-8">Select the final output artifacts that the agents will construct.</p>
            
            <div className="grid gap-3">
              {/* @ts-ignore */}
              {ARTIFACT_OPTIONS[persona]?.map((opt) => (
                <button
                  key={opt.id}
                  onClick={() => handleArtifactToggle(opt.id)}
                  className={`text-left p-4 rounded-xl border flex items-center justify-between transition-colors cursor-pointer ${
                    selectedArtifacts.includes(opt.id)
                      ? 'bg-indigo-50 border-indigo-600 text-indigo-700'
                      : 'bg-white border-slate-200 text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <span className="font-semibold text-sm">{opt.label}</span>
                  <div className={`w-5 h-5 rounded-md border flex items-center justify-center ${
                    selectedArtifacts.includes(opt.id) ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-slate-300'
                  }`}>
                    {selectedArtifacts.includes(opt.id) && (
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* STEP 7: Review & Final Checklist */}
        {step === 7 && (
          <div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-600" /> Review Brief & Sources
            </h2>
            <p className="text-sm text-slate-500 mb-8">Verify the selected parameters, custom context files, and bibliography list before launching.</p>
            
            <div className="space-y-6">
              {/* Summary metadata */}
              <div className="grid grid-cols-2 gap-4 text-sm p-5 rounded-2xl bg-slate-50 border border-slate-200/60">
                <div>
                  <span className="text-slate-400 block text-xs font-bold uppercase tracking-wider mb-0.5">Persona Crew</span>
                  <span className="text-slate-800 capitalize font-semibold">{persona.replace('_', ' ')}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-xs font-bold uppercase tracking-wider mb-0.5">Topic</span>
                  <span className="text-slate-800 font-semibold truncate block max-w-[250px]">{topic}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-xs font-bold uppercase tracking-wider mb-0.5">Tone & Audience</span>
                  <span className="text-slate-800 font-semibold">{tone} / {audience}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-xs font-bold uppercase tracking-wider mb-0.5">Artifacts</span>
                  <span className="text-slate-800 font-semibold">{selectedArtifacts.length} selected</span>
                </div>
              </div>

              {/* Curated Citations/Sources check-preview list */}
              {selectedSources.length > 0 && (
                <div className="space-y-2.5">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-450 block">Target Bibliography to Cite ({selectedSources.length})</span>
                  <div className="border border-slate-200 rounded-xl divide-y divide-slate-100 max-h-[140px] overflow-y-auto bg-white px-4">
                    {selectedSources.map((s, i) => (
                      <div key={i} className="py-2.5 flex items-center justify-between text-xs text-slate-700">
                        <span className="font-semibold truncate max-w-[320px]">{s.title}</span>
                        <span className="text-[10px] text-slate-400 font-mono px-2 py-0.5 bg-slate-50 border border-slate-150 rounded">{s.domain}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Uploaded Context check */}
              {contextText && (
                <div className="space-y-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-455 block">Uploaded Context Preview</span>
                  <div className="border border-slate-200 rounded-xl bg-slate-50 p-4 max-h-[100px] overflow-y-auto text-xs text-slate-500 font-mono whitespace-pre-wrap">
                    {contextText}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Wizard Navigation Panel */}
        <div className="flex items-center justify-between mt-10 border-t border-slate-200 pt-6">
          <button
            onClick={() => setStep(step - 1)}
            disabled={step === 1 || submitting || parsingDocument}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-200 hover:border-slate-350 text-sm font-semibold text-slate-500 hover:text-slate-700 disabled:opacity-30 disabled:pointer-events-none transition-all cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" /> Back
          </button>

          {step === 2 ? (
            <button
              onClick={handleDiscoverSources}
              disabled={!topic.trim() || loadingSources}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold primary-button text-sm disabled:opacity-50 cursor-pointer"
            >
              {loadingSources ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Discovering Sources...
                </>
              ) : (
                <>
                  Discover Sources <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          ) : step === 7 ? (
            <button
              onClick={handleLaunch}
              disabled={submitting}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold primary-button text-sm disabled:opacity-50 cursor-pointer"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Deploying Crew...
                </>
              ) : (
                <>
                  Launch Deep Researcher <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          ) : (
            <button
              onClick={() => setStep(step + 1)}
              disabled={(step === 3 && selectedSources.length === 0) || (step === 6 && selectedArtifacts.length === 0) || parsingDocument}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold primary-button text-sm disabled:opacity-50 cursor-pointer"
            >
              Continue <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
