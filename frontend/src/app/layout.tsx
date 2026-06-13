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
