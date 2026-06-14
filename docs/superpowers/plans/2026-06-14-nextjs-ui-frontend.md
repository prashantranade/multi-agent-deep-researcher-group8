# Next.js UI Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a state-of-the-art, premium dark-mode Next.js UI frontend to serve as the user-facing product for the multi-agent deep researcher.

**Architecture:** A decoupled Next.js App Router project under `/frontend` that communicates with the FastAPI backend REST API. It maintains wizard state client-side, polls task status asynchronously, renders a live node progress pipeline, logs agent outputs, and renders markdown artifacts with premium styling.

**Tech Stack:** Next.js (App Router), React, Tailwind CSS, TypeScript, Lucide Icons, React Markdown.

---

## Proposed Changes & Tasks

### Task 1: Initialize Next.js Project

**Files:**
- Create: `frontend` (Directory containing the Next.js project)

- [ ] **Step 1: Bootstrap the Next.js app in /frontend**
  Create the folder `frontend/` and initialize the Next.js app inside it using `create-next-app` in non-interactive mode.
  Run:
  `npx -y create-next-app@latest frontend --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --disable-git --yes`
  Expected: Success, creating `frontend` folder containing boilerplate files.

- [ ] **Step 2: Install UI dependencies**
  Install lucide-react and react-markdown inside the frontend app.
  Run:
  `cd frontend; npm install lucide-react react-markdown`
  Expected: Package installation completes successfully.

- [ ] **Step 3: Commit initialization**
  ```bash
  git add frontend/package.json
  git commit -m "feat: initialize frontend next.js app with dependencies"
  ```

---

### Task 2: Setup Tailwind & Global Styles (Design System)

**Files:**
- Modify: `frontend/src/app/globals.css`
- Modify: `frontend/tailwind.config.ts`

- [ ] **Step 1: Update globals.css with premium glassmorphism classes**
  Replace contents of `frontend/src/app/globals.css` with a sleek dark-theme and custom glassmorphism utilities.
  
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;

  :root {
    --foreground-rgb: 248, 250, 252;
    --background-start-rgb: 8, 10, 18;
    --background-end-rgb: 3, 4, 8;
  }

  body {
    color: rgb(var(--foreground-rgb));
    background: linear-gradient(
        to bottom,
        transparent,
        rgb(var(--background-end-rgb))
      )
      rgb(var(--background-start-rgb));
    min-height: 100vh;
    font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  }

  /* Glassmorphism custom components */
  .glass-panel {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .glass-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .glass-card:hover {
    background: rgba(30, 41, 59, 0.65);
    border-color: rgba(99, 102, 241, 0.35);
    box-shadow: 0 0 25px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
  }

  .glow-button {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3);
    transition: all 0.2s ease;
  }

  .glow-button:hover:not(:disabled) {
    box-shadow: 0 0 25px rgba(99, 102, 241, 0.6);
    transform: scale(1.02);
  }

  .glow-button:active:not(:disabled) {
    transform: scale(0.98);
  }

  .live-glow {
    box-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
  }
  ```

- [ ] **Step 2: Verify Tailwind Config**
  Verify configuration is correct. No changes required to `tailwind.config.ts` unless custom colors are wanted; the default classes from Tailwind suffice.
  
- [ ] **Step 3: Commit styling foundation**
  ```bash
  git add frontend/src/app/globals.css
  git commit -m "style: establish dark mode and glassmorphic design system"
  ```

---

### Task 3: API Service Utility & Types

**Files:**
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/lib/api.ts`

- [ ] **Step 1: Create types.ts**
  Define structural interfaces representing sources, brief details, execution notes, and task progress.
  
  ```typescript
  // frontend/src/lib/types.ts

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
  ```

- [ ] **Step 2: Create api.ts wrapper**
  Create the service client to interact with `http://localhost:8000`.
  
  ```typescript
  // frontend/src/lib/api.ts
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
    if (!res.ok) throw new Error('Failed to retrieve task status');
    return res.json();
  }

  export async function getResearchResults(taskId: string): Promise<TaskResultsResponse> {
    const res = await fetch(`${API_BASE}/research/results/${taskId}`);
    if (!res.ok) throw new Error('Failed to retrieve task results');
    return res.json();
  }
  ```

- [ ] **Step 3: Commit API service layer**
  ```bash
  git add frontend/src/lib/types.ts frontend/src/lib/api.ts
  git commit -m "feat: add frontend TypeScript types and api client wrapper"
  ```

---

### Task 4: Layout & Navigation Bar

**Files:**
- Modify: `frontend/src/app/layout.tsx`

- [ ] **Step 1: Replace layout.tsx**
  Implement a beautiful premium global navbar with logo, link to Start Research, and History logs. Include visual glowing background blur gradients.
  
  ```tsx
  // frontend/src/app/layout.tsx
  import type { Metadata } from "next";
  import "./globals.css";
  import Link from "next/link";
  import { Compass, History, Zap } from "lucide-react";

  export const metadata: Metadata = {
    title: "Deep Researcher — Agentic Insights Platform",
    description: "Multi-agent strategic researcher powered by LangGraph, FastAPI and React.",
  };

  export default function RootLayout({
    children,
  }: Readonly<{
    children: React.ReactNode;
  }>) {
    return (
      <html lang="en">
        <body className="antialiased overflow-x-hidden relative">
          {/* Ambient Glowing Background Elements */}
          <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-indigo-500/10 blur-[120px] pointer-events-none" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-purple-500/10 blur-[120px] pointer-events-none" />

          {/* Navigation Bar */}
          <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-md shadow-indigo-500/20 group-hover:scale-105 transition-transform duration-200">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg bg-gradient-to-r from-slate-100 via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                DEEP RESEARCHER
              </span>
            </Link>

            <nav className="flex gap-6">
              <Link href="/research" className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-indigo-400 transition-colors">
                <Compass className="w-4 h-4" />
                Research Panel
              </Link>
              <Link href="/history" className="flex items-center gap-1.5 text-sm font-medium text-slate-300 hover:text-indigo-400 transition-colors">
                <History className="w-4 h-4" />
                Research Logs
              </Link>
            </nav>
          </header>

          {/* Main Area */}
          <main className="max-w-7xl mx-auto px-6 py-10 relative z-10">
            {children}
          </main>
        </body>
      </html>
    );
  }
  ```

- [ ] **Step 2: Commit layout**
  ```bash
  git add frontend/src/app/layout.tsx
  git commit -m "feat: design global navbar and background glows in root layout"
  ```

---

### Task 5: Premium Homepage

**Files:**
- Modify: `frontend/src/app/page.tsx`

- [ ] **Step 1: Replace page.tsx**
  Implement a striking marketing landing page with glass persona cards showing features, target metrics, and a large call-to-action button to initiate the deep research wizard.
  
  ```tsx
  // frontend/src/app/page.tsx
  import Link from "next/link";
  import { Compass, Users, Sparkles, BookOpen, BarChart } from "lucide-react";

  export default function Home() {
    const personas = [
      {
        title: "Product Manager",
        icon: <BarChart className="w-6 h-6 text-indigo-400" />,
        desc: "Builds comprehensive competitive analysis, opportunity size matrices, product requirement insights, and detailed research briefs.",
        highlights: ["Opportunity Size Matrix", "PRD Insights", "Competitive Summary"]
      },
      {
        title: "Content Creator",
        icon: <Sparkles className="w-6 h-6 text-purple-400" />,
        desc: "Generates trend-focused content briefs, multi-platform social draft copy, captions, hashtags, and social media calendar entries.",
        highlights: ["Content Briefs", "Social Drafts & Copy", "Calendar Entries"]
      },
      {
        title: "Bharat Desha (Tourism)",
        icon: <BookOpen className="w-6 h-6 text-emerald-400" />,
        desc: "Researches regional Indian tourism itineraries, destination guide books, wellness travel suggestions, and localized social media content.",
        highlights: ["SEO Keyword Planning", "Custom Itineraries", "Destination Guides"]
      }
    ];

    return (
      <div className="flex flex-col items-center justify-center text-center mt-12 mb-20">
        {/* Glow Badge */}
        <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900/80 border border-indigo-500/20 text-xs font-semibold text-indigo-400 mb-8 backdrop-blur-md">
          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          Powered by LangGraph & FastAPI
        </div>

        {/* Hero Title */}
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl leading-tight mb-6 bg-gradient-to-b from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
          Strategic Multi-Agent <br />
          <span className="bg-gradient-to-r from-indigo-400 via-purple-500 to-emerald-400 bg-clip-text">Deep Researcher</span>
        </h1>

        <p className="text-lg text-slate-400 max-w-2xl leading-relaxed mb-12">
          Deploy groups of autonomous stateful agents to discover sources, perform semantic analysis, and compile market-ready artifacts.
        </p>

        {/* Start Button */}
        <Link href="/research" className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold glow-button text-base mb-20 cursor-pointer">
          <Compass className="w-5 h-5" />
          Deploy Agentic Crew
        </Link>

        {/* Persona Columns */}
        <div className="w-full max-w-6xl">
          <h2 className="text-2xl font-bold mb-10 text-slate-300 flex items-center justify-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            Specialized Persona Crews
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {personas.map((p, i) => (
              <div key={i} className="glass-card rounded-2xl p-6 text-left flex flex-col justify-between">
                <div>
                  <div className="p-3 bg-slate-900/60 w-fit rounded-xl border border-slate-800/80 mb-6">
                    {p.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3 text-slate-100">{p.title}</h3>
                  <p className="text-sm text-slate-400 leading-relaxed mb-6">{p.desc}</p>
                </div>
                <div className="border-t border-slate-800/80 pt-4">
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">Outputs:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {p.highlights.map((h, j) => (
                      <span key={j} className="text-xs px-2 py-1 rounded bg-slate-900/80 border border-slate-800/80 text-slate-300">
                        {h}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }
  ```

- [ ] **Step 2: Commit homepage**
  ```bash
  git add frontend/src/app/page.tsx
  git commit -m "feat: design premium landing page with persona features"
  ```

---

### Task 6: Guided Research Wizard

**Files:**
- Create: `frontend/src/app/research/page.tsx`

- [ ] **Step 1: Write research/page.tsx**
  Implement the 6-step stateful wizard client-side that prompts users for the topic, fetches discoverable sources, selects configuring fields, checks artifact types, and launches the task.
  
  ```tsx
  // frontend/src/app/research/page.tsx
  'use client';

  import { useState } from 'react';
  import { useRouter } from 'next/navigation';
  import { discoverSources, startResearch } from '@/lib/api';
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
        {/* Step Indicator Header */}
        <div className="flex items-center justify-between mb-12 border-b border-slate-800/80 pb-6">
          {[1, 2, 3, 4, 5, 6].map((s) => (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                step === s ? 'bg-indigo-500 text-white ring-4 ring-indigo-500/20' :
                step > s ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30' :
                'bg-slate-900 border border-slate-800 text-slate-500'
              }`}>
                {s}
              </div>
              <span className={`text-xs font-medium hidden sm:inline ${step === s ? 'text-slate-200' : 'text-slate-500'}`}>
                {s === 1 && 'Persona'}
                {s === 2 && 'Topic'}
                {s === 3 && 'Sources'}
                {s === 4 && 'Parameters'}
                {s === 5 && 'Artifacts'}
                {s === 6 && 'Review'}
              </span>
              {s < 6 && <div className="w-4 sm:w-12 h-px bg-slate-800" />}
            </div>
          ))}
        </div>

        {/* Wizard Card Body */}
        <div className="glass-panel rounded-3xl p-8 mb-6 shadow-2xl relative overflow-hidden">
          
          {/* STEP 1: Persona */}
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <User className="w-5 h-5 text-indigo-400" /> Choose Persona Crew
              </h2>
              <p className="text-sm text-slate-400 mb-8">Select the strategic perspective that will analyze your research topic.</p>
              
              <div className="grid gap-4">
                {PERSONAS.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => selectPersona(p.id)}
                    className={`text-left p-6 rounded-2xl transition-all duration-200 border cursor-pointer ${
                      persona === p.id 
                        ? 'bg-indigo-500/10 border-indigo-500 shadow-indigo-500/5' 
                        : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700/80'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-lg text-slate-100">{p.name}</span>
                      <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${
                        persona === p.id ? 'border-indigo-500 bg-indigo-500' : 'border-slate-700'
                      }`}>
                        {persona === p.id && <div className="w-2 h-2 rounded-full bg-white" />}
                      </div>
                    </div>
                    <p className="text-sm text-slate-400 leading-relaxed">{p.desc}</p>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* STEP 2: Topic input */}
          {step === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <Globe className="w-5 h-5 text-indigo-400" /> Enter Research Topic
              </h2>
              <p className="text-sm text-slate-400 mb-8">Specify the core search query. Deep Researcher will fetch web resources to build local memory.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">Research Topic</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g. Sustainable ecotourism projects in Rajasthan or GenAI trends in sales enablement"
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3.5 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-2">Suggested topics:</span>
                  <div className="flex flex-col gap-2 text-sm text-slate-400">
                    <button onClick={() => setTopic("Jaipur cultural tourism itineraries")} className="text-left hover:text-indigo-400 transition-colors">➔ Jaipur cultural tourism itineraries</button>
                    <button onClick={() => setTopic("Comparison of LLM evaluation frameworks")} className="text-left hover:text-indigo-400 transition-colors">➔ Comparison of LLM evaluation frameworks</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: Curate Sources */}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <Globe className="w-5 h-5 text-indigo-400" /> Curate Discoverable Sources
              </h2>
              <p className="text-sm text-slate-400 mb-8">Verify and curate the list of confidence-scored web resources that our agents will digest.</p>
              
              <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
                {sources.map((s, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-start justify-between gap-4">
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
                        className="mt-1 rounded border-slate-800 text-indigo-600 focus:ring-indigo-500"
                      />
                      <div>
                        <span className="font-semibold text-slate-200 text-sm block leading-snug mb-1">{s.title}</span>
                        <a href={s.url} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-400 hover:underline block mb-1 truncate max-w-[450px]">{s.url}</a>
                        {s.date && <span className="text-xs text-slate-500">{s.date}</span>}
                      </div>
                    </div>
                    {s.overall_score !== undefined && (
                      <span className="text-xs font-semibold px-2 py-1 rounded-md bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                        Score: {Math.round(s.overall_score * 100)}
                      </span>
                    )}
                  </div>
                ))}
                {sources.length === 0 && (
                  <div className="text-center py-10 text-slate-500 text-sm">No sources discovered. Continue to use default web search backup.</div>
                )}
              </div>
            </div>
          )}

          {/* STEP 4: Configuration Parameters */}
          {step === 4 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <Settings className="w-5 h-5 text-indigo-400" /> Setup Configuration
              </h2>
              <p className="text-sm text-slate-400 mb-8">Adjust parameters like target audience segment, communication tone, and depth of analysis.</p>
              
              <div className="grid sm:grid-cols-2 gap-6">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">Audience Segment</label>
                  <select
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    {/* @ts-ignore */}
                    {AUDIENCES[persona]?.map((a) => (
                      <option key={a} value={a}>{a}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">Communication Tone</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                  >
                    {/* @ts-ignore */}
                    {TONES[persona]?.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>

                <div className="sm:col-span-2">
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-3">Research Depth</label>
                  <div className="grid grid-cols-3 gap-3">
                    {['quick', 'standard', 'deep'].map((d) => (
                      <button
                        key={d}
                        onClick={() => setDepth(d)}
                        className={`py-3 rounded-xl border text-sm font-semibold capitalize transition-all cursor-pointer ${
                          depth === d
                            ? 'bg-indigo-500/10 border-indigo-500 text-indigo-400'
                            : 'bg-slate-900/60 border-slate-800/80 text-slate-400 hover:border-slate-700/80'
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

          {/* STEP 5: Selected Artifacts */}
          {step === 5 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <CheckSquare className="w-5 h-5 text-indigo-400" /> Target Artifacts
              </h2>
              <p className="text-sm text-slate-400 mb-8">Select the final output artifacts that the agents will construct.</p>
              
              <div className="grid gap-3">
                {/* @ts-ignore */}
                {ARTIFACT_OPTIONS[persona]?.map((opt) => (
                  <button
                    key={opt.id}
                    onClick={() => handleArtifactToggle(opt.id)}
                    className={`text-left p-4 rounded-xl border flex items-center justify-between transition-colors cursor-pointer ${
                      selectedArtifacts.includes(opt.id)
                        ? 'bg-indigo-500/10 border-indigo-500 text-indigo-400'
                        : 'bg-slate-900/60 border-slate-800/80 text-slate-300 hover:border-slate-700/80'
                    }`}
                  >
                    <span className="font-medium text-sm text-slate-200">{opt.label}</span>
                    <div className={`w-5 h-5 rounded-md border flex items-center justify-center ${
                      selectedArtifacts.includes(opt.id) ? 'border-indigo-500 bg-indigo-500 text-white' : 'border-slate-700'
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

          {/* STEP 6: Review & Context */}
          {step === 6 && (
            <div>
              <h2 className="text-2xl font-bold text-slate-100 mb-2 flex items-center gap-2">
                <FileText className="w-5 h-5 text-indigo-400" /> Review Brief & Add Context
              </h2>
              <p className="text-sm text-slate-400 mb-8">Optionally insert custom document snippets, raw notes, or target requirements before deploying the crew.</p>
              
              <div className="space-y-6">
                <div>
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-2">Additional Context & Documents (Optional)</label>
                  <textarea
                    rows={4}
                    value={contextText}
                    onChange={(e) => setContextText(e.target.value)}
                    placeholder="Paste transcripts, background details, company URLs, or constraints..."
                    className="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-slate-100 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition-colors resize-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm p-5 rounded-2xl bg-slate-900/40 border border-slate-800/60">
                  <div>
                    <span className="text-slate-500 block text-xs font-bold uppercase tracking-wider">Persona Crew</span>
                    <span className="text-slate-200 capitalize font-medium">{persona.replace('_', ' ')}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-xs font-bold uppercase tracking-wider">Topic</span>
                    <span className="text-slate-200 font-medium truncate block max-w-[250px]">{topic}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-xs font-bold uppercase tracking-wider">Tone & Audience</span>
                    <span className="text-slate-200 font-medium">{tone} / {audience}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-xs font-bold uppercase tracking-wider">Artifacts Selected</span>
                    <span className="text-slate-200 font-medium">{selectedArtifacts.length} total</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Wizard Navigation Panel */}
          <div className="flex items-center justify-between mt-10 border-t border-slate-800/80 pt-6">
            <button
              onClick={() => setStep(step - 1)}
              disabled={step === 1 || submitting}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-slate-800/80 hover:border-slate-700/80 text-sm font-semibold text-slate-400 hover:text-slate-200 disabled:opacity-30 disabled:pointer-events-none transition-all cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" /> Back
            </button>

            {step === 2 ? (
              <button
                onClick={handleDiscoverSources}
                disabled={!topic.trim() || loadingSources}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold glow-button text-sm disabled:opacity-50 cursor-pointer"
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
            ) : step === 6 ? (
              <button
                onClick={handleLaunch}
                disabled={submitting}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold glow-button text-sm disabled:opacity-50 cursor-pointer"
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
                disabled={(step === 3 && selectedSources.length === 0) || (step === 5 && selectedArtifacts.length === 0)}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-white font-semibold glow-button text-sm disabled:opacity-50 cursor-pointer"
              >
                Continue <ChevronRight className="w-4 h-4" />
              </button>
            )}
          </div>

        </div>
      </div>
    );
  }
  ```

- [ ] **Step 2: Commit wizard component**
  ```bash
  git add frontend/src/app/research/page.tsx
  git commit -m "feat: implement step-by-step stateful research wizard"
  ```

---

### Task 7: Live Execution Tracker & Artifact Viewer

**Files:**
- Create: `frontend/src/app/research/[task_id]/page.tsx`

- [ ] **Step 1: Write research/[task_id]/page.tsx**
  Implement the polling, the horizontal node execution graph pipeline, the scrollable Green Terminal logs console, and the markdown output layout with accordions for citations.
  
  ```tsx
  // frontend/src/app/research/[task_id]/page.tsx
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
    // @ts-ignore
    const pipelineNodes = PERSONA_PIPELINES[persona] || PERSONA_PIPELINES.product_manager;

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
              {pipelineNodes.map((node, index) => {
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
            <div className="p-6 bg-slate-950 font-mono text-xs text-purple-400 space-y-3 h-[250px] overflow-y-auto">
              {statusData.notes && statusData.notes.map((note, i) => (
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
  ```

- [ ] **Step 2: Commit tracker component**
  ```bash
  git add frontend/src/app/research/[task_id]/page.tsx
  git commit -m "feat: implement visual node graphs and monospace logs tracker screen"
  ```

---

### Task 8: History Logs Directory

**Files:**
- Create: `frontend/src/app/history/page.tsx`

- [ ] **Step 1: Write history/page.tsx**
  Implement the storage rendering page detailing prior tasks, timestamps, statuses, and links back.
  
  ```tsx
  // frontend/src/app/history/page.tsx
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
  ```

- [ ] **Step 2: Commit history page**
  ```bash
  git add frontend/src/app/history/page.tsx
  git commit -m "feat: implement research history logger client-side"
  ```

---

## Verification Plan

### Automated Verification
- Verify code compiles by running Next.js build:
  `cd frontend; npm run build`

### Manual Verification
1. Boot the FastAPI backend:
   `uvicorn api:app --reload --port 8000`
2. Start the Next.js frontend dev server:
   `cd frontend; npm run dev`
3. Load `http://localhost:3000` in the browser.
4. Step through the 6-step guided wizard:
   - Select Content Creator persona.
   - Enter topic "Jaipur historical architectures".
   - Click "Discover Sources".
   - Select/Deselect sources.
   - Select "Witty" tone and "SaaS Founders" audience.
   - Check "captions" and "social_draft" artifacts.
   - Hit "Launch Deep Researcher".
5. Verify redirection to `/research/[task_id]` and that it polls successfully.
6. Check that the live pipeline progresses through `retrieve` -> `analyse` -> `generate_artifacts` matching the terminal notes.
7. Confirm that the final output details are rendered in a gorgeous card layout with Copy/Download buttons and citation details.
