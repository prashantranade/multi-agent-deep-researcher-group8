import Link from "next/link";
import { Compass, Users, Sparkles, BookOpen, BarChart } from "lucide-react";

export default function Home() {
  const personas = [
    {
      title: "Product Manager",
      icon: <BarChart className="w-6 h-6 text-indigo-600" />,
      desc: "Builds comprehensive competitive analysis, opportunity size matrices, product requirement insights, and detailed research briefs.",
      highlights: ["Opportunity Size Matrix", "PRD Insights", "Competitive Summary"]
    },
    {
      title: "Content Creator",
      icon: <Sparkles className="w-6 h-6 text-purple-600" />,
      desc: "Generates trend-focused content briefs, multi-platform social draft copy, captions, hashtags, and social media calendar entries.",
      highlights: ["Content Briefs", "Social Drafts & Copy", "Calendar Entries"]
    },
    {
      title: "Bharat Desha (Tourism)",
      icon: <BookOpen className="w-6 h-6 text-emerald-600" />,
      desc: "Researches regional Indian tourism itineraries, destination guide books, wellness travel suggestions, and localized social media content.",
      highlights: ["SEO Keyword Planning", "Custom Itineraries", "Destination Guides"]
    }
  ];

  return (
    <div className="flex flex-col items-center justify-center text-center mt-12 mb-20">
      {/* Light Badge */}
      <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white border border-slate-200 text-xs font-semibold text-slate-700 mb-8 shadow-sm">
        <Sparkles className="w-3.5 h-3.5 text-indigo-600 animate-pulse" />
        Multi-Agent System
      </div>

      {/* Hero Title */}
      <h1 className="text-5xl md:text-7xl font-black tracking-tight max-w-4xl leading-tight mb-6 text-slate-900">
        Strategic Multi-Agent <br />
        <span className="text-indigo-600">Deep Researcher</span>
      </h1>

      <p className="text-lg text-slate-600 max-w-2xl leading-relaxed mb-12">
        Deploy groups of autonomous stateful agents to discover sources, perform semantic analysis, and compile market-ready reports.
      </p>

      {/* Start Button */}
      <Link href="/research" className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-white font-semibold primary-button text-base mb-20 cursor-pointer">
        <Compass className="w-5 h-5" />
        Deploy Agentic Crew
      </Link>

      {/* Persona Columns */}
      <div className="w-full max-w-6xl">
        <h2 className="text-2xl font-bold mb-10 text-slate-800 flex items-center justify-center gap-2">
          <Users className="w-5 h-5 text-indigo-600" />
          Specialized Persona Crews
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {personas.map((p, i) => (
            <div key={i} className="clean-card rounded-2xl p-6 text-left flex flex-col justify-between">
              <div>
                <div className="p-3 bg-slate-50 w-fit rounded-xl border border-slate-100 mb-6">
                  {p.icon}
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-900">{p.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed mb-6">{p.desc}</p>
              </div>
              <div className="border-t border-slate-100 pt-4">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">Outputs:</span>
                <div className="flex flex-wrap gap-1.5">
                  {p.highlights.map((h, j) => (
                    <span key={j} className="text-xs px-2.5 py-1 rounded-md bg-slate-50 border border-slate-150 text-slate-600 font-medium">
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
