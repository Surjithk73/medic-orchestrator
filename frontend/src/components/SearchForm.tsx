"use client";

import { useState } from "react";
import { Activity, Microscope, Sparkles, Zap, Shield, TrendingUp } from "lucide-react";
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
    <div className="w-full max-w-6xl mx-auto">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-6">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <span className="text-sm text-indigo-300 font-medium">Powered by Multi-Agent AI</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
          <span className="text-zinc-100">Discover</span>
          <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Repurposing Opportunities
          </span>
        </h1>
        
        <p className="text-zinc-400 text-xl max-w-3xl mx-auto leading-relaxed">
          Autonomous intelligence platform analyzing clinical trials, patents, regulatory data, and market insights to identify novel therapeutic applications.
        </p>
      </motion.div>

      {/* Search Bar */}
      <motion.form 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        onSubmit={handleSubmit} 
        className="relative group mb-8 max-w-3xl mx-auto"
      >
        <div className={`absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-xl blur opacity-20 group-hover:opacity-30 transition duration-1000 ${isFocused ? 'opacity-40' : ''}`}></div>
        <div className="relative flex items-center bg-zinc-900/90 backdrop-blur-xl ring-1 ring-white/10 rounded-xl p-2 shadow-2xl">
          <div className="pl-3 pr-2 text-zinc-400">
            <Microscope className="w-5 h-5" />
          </div>
          <input
            type="text"
            value={molecule}
            onChange={(e) => setMolecule(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="Enter molecule or drug name (e.g., Aspirin, Metformin)..."
            className="flex-1 bg-transparent border-none text-zinc-100 placeholder-zinc-500 focus:outline-none focus:ring-0 text-base py-3 px-2"
          />
          <button
            type="submit"
            disabled={!molecule.trim()}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white disabled:opacity-50 disabled:cursor-not-allowed rounded-lg px-6 py-2.5 font-semibold transition-all flex items-center gap-2 shadow-lg shadow-indigo-500/25"
          >
            <span>Analyze</span>
            <Activity className="w-4 h-4" />
          </button>
        </div>
      </motion.form>

      {/* Cached Molecules */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-16"
      >
        <p className="text-center text-sm text-zinc-500 mb-4">
          Pre-analyzed molecules cached for <span className="text-indigo-400 font-medium">instant access</span>:
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          {['Metformin', 'Ibuprofen', 'Thalidomide'].map(term => (
            <button 
              key={term} 
              onClick={() => setMolecule(term)}
              className="group px-6 py-3 rounded-xl bg-gradient-to-r from-indigo-500/10 to-purple-500/10 hover:from-indigo-500/20 hover:to-purple-500/20 text-zinc-300 hover:text-white transition-all border border-indigo-500/30 hover:border-indigo-400/50 font-medium relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/0 via-indigo-500/10 to-indigo-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
              <span className="relative flex items-center gap-2">
                {term}
                <Zap className="w-4 h-4 text-indigo-400" />
              </span>
            </button>
          ))}
        </div>
      </motion.div>

      {/* Features Grid */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <div className="group relative p-8 rounded-2xl bg-gradient-to-br from-zinc-900/50 to-zinc-900/30 border border-zinc-800/50 hover:border-indigo-500/30 transition-all duration-300">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-indigo-600/20 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Zap className="w-7 h-7 text-indigo-400" />
            </div>
            <h3 className="text-xl font-bold text-zinc-100 mb-3">Lightning Fast</h3>
            <p className="text-zinc-400 leading-relaxed">
              Cached results load instantly. New analyses complete in 2-3 minutes with real-time progress updates.
            </p>
          </div>
        </div>

        <div className="group relative p-8 rounded-2xl bg-gradient-to-br from-zinc-900/50 to-zinc-900/30 border border-zinc-800/50 hover:border-purple-500/30 transition-all duration-300">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <Shield className="w-7 h-7 text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-zinc-100 mb-3">Multi-Agent AI</h3>
            <p className="text-zinc-400 leading-relaxed">
              4 specialized agents analyze clinical trials, patents, market data, and regulatory information in parallel.
            </p>
          </div>
        </div>

        <div className="group relative p-8 rounded-2xl bg-gradient-to-br from-zinc-900/50 to-zinc-900/30 border border-zinc-800/50 hover:border-pink-500/30 transition-all duration-300">
          <div className="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-pink-500/20 to-pink-600/20 flex items-center justify-center mb-5 group-hover:scale-110 transition-transform">
              <TrendingUp className="w-7 h-7 text-pink-400" />
            </div>
            <h3 className="text-xl font-bold text-zinc-100 mb-3">Actionable Insights</h3>
            <p className="text-zinc-400 leading-relaxed">
              Comprehensive reports with opportunity scores, citations, and strategic recommendations for decision-making.
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
