"use client";

import { useState } from "react";
import { Activity, Microscope } from "lucide-react";
import { motion } from "framer-motion";

export default function SearchForm({ onSearch }: { onSearch: (molecule: string) => void }) {
  const [molecule, setMolecule] = useState("");
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (molecule.trim()) {
      onSearch(molecule.trim());
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 mb-8">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-8"
      >
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-zinc-100">
          Discover Repurposing<br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
            Opportunities
          </span>
        </h1>
        <p className="text-zinc-400 text-lg max-w-xl mx-auto">
          Multi-agent orchestration analyzing clinical, patent, regulatory, and market domains to identify novel indications.
        </p>
      </motion.div>

      <form onSubmit={handleSubmit} className="relative group">
        <div className={`absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200 ${isFocused ? 'opacity-75 duration-200' : ''}`}></div>
        <div className="relative flex items-center bg-[#121214] ring-1 ring-white/10 rounded-2xl p-2 shadow-2xl">
          <div className="pl-4 pr-3 text-zinc-400">
            <Microscope className="w-6 h-6" />
          </div>
          <input
            type="text"
            value={molecule}
            onChange={(e) => setMolecule(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Enter molecule or drug name (e.g., Aspirin, Metformin)..."
            className="flex-1 bg-transparent border-none text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-0 text-lg py-3"
          />
          <button
            type="submit"
            disabled={!molecule.trim()}
            className="bg-zinc-100 text-zinc-900 hover:bg-white disabled:opacity-50 disabled:cursor-not-allowed rounded-xl px-6 py-3 font-semibold transition-all flex items-center gap-2"
          >
            <span>Analyze</span>
            <Activity className="w-5 h-5" />
          </button>
        </div>
      </form>

      <div className="mt-6 space-y-2">
        <p className="text-center text-sm text-zinc-400">
          Pre-analyzed molecules cached for instant access:
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
          {['Metformin', 'Ibuprofen', 'Thalidomide'].map(term => (
            <button 
              key={term} 
              onClick={() => {
                setMolecule(term);
                onSearch(term);
              }}
              className="px-4 py-2 rounded-full bg-gradient-to-r from-indigo-500/10 to-purple-500/10 hover:from-indigo-500/20 hover:to-purple-500/20 text-zinc-300 hover:text-white transition-all border border-indigo-500/30 hover:border-indigo-400/50 font-medium"
            >
              {term} ⚡
            </button>
          ))}
        </div>
      </div>

      {/* Features Section */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <div className="text-center p-6 rounded-2xl bg-zinc-900/30 border border-zinc-800/50">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="font-semibold text-zinc-200 mb-2">Lightning Fast</h3>
          <p className="text-sm text-zinc-500">Cached results load instantly. New analyses complete in 2-3 minutes.</p>
        </div>

        <div className="text-center p-6 rounded-2xl bg-zinc-900/30 border border-zinc-800/50">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h3 className="font-semibold text-zinc-200 mb-2">Multi-Agent AI</h3>
          <p className="text-sm text-zinc-500">4 specialized agents analyze clinical, patent, market, and regulatory data.</p>
        </div>

        <div className="text-center p-6 rounded-2xl bg-zinc-900/30 border border-zinc-800/50">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="font-semibold text-zinc-200 mb-2">Comprehensive Reports</h3>
          <p className="text-sm text-zinc-500">Detailed analysis with citations, scores, and actionable insights.</p>
        </div>
      </div>
    </div>
  );
}
