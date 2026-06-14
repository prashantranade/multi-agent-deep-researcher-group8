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
      <body className="antialiased overflow-x-hidden relative bg-slate-50/50">
        {/* Soft Ambient Light Background Glows */}
        <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-slate-100/50 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-indigo-50/30 blur-[120px] pointer-events-none" />

        {/* Clean Minimalist Navigation Bar */}
        <header className="sticky top-0 z-50 clean-panel border-b border-slate-200/80 px-6 py-4 flex items-center justify-between bg-white/85">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="p-2 rounded-xl bg-slate-900 text-white shadow-sm group-hover:scale-105 transition-transform duration-200">
              <Zap className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg text-slate-800 tracking-tight">
              DEEP RESEARCHER
            </span>
          </Link>

          <nav className="flex gap-6">
            <Link href="/research" className="flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors">
              <Compass className="w-4 h-4" />
              Research Panel
            </Link>
            <Link href="/history" className="flex items-center gap-1.5 text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors">
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
