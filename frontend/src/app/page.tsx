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
