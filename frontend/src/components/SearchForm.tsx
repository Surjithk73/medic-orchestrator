"use client";

import { useState } from "react";
import { Search, Activity, Microscope, Filter } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

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

      <div className="mt-6 flex flex-wrap items-center justify-center gap-2 text-sm text-zinc-500">
        <span>Popular:</span>
        {['Ketamine', 'Thalidomide', 'Sildenafil'].map(term => (
          <button 
            key={term} 
            onClick={() => setMolecule(term)}
            className="px-3 py-1 rounded-full bg-zinc-800/50 hover:bg-zinc-800 hover:text-zinc-300 transition-colors border border-zinc-700/50"
          >
            {term}
          </button>
        ))}
      </div>
    </div>
  );
}
