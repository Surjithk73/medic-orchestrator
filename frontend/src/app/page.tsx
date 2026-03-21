"use client";

import { useState } from "react";
import SearchForm from "@/components/SearchForm";
import ProgressViewer from "@/components/ProgressViewer";
import ReportViewer from "@/components/ReportViewer";
import { motion, AnimatePresence } from "framer-motion";
import { API_BASE_URL } from "@/lib/config";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [molecule, setMolecule] = useState<string | null>(null);
  const [mode, setMode] = useState<"search" | "researching" | "report">("search");

  const handleSearch = async (query: string) => {
    setMolecule(query);
    setMode("researching");
    
    try {
      // 1. Trigger backend orchestrator 
      const res = await fetch(`${API_BASE_URL}/api/research/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ molecule: query })
      });
      
      const data = await res.json();
      console.log("API Response:", data);  // DEBUG
      
      const newSessionId = data.session_id || "mock-session-1234";
      setSessionId(newSessionId);
      
      // Check if report was served from cache
      if (data.from_cache === true) {
        console.log("✅ Cache hit! Showing report immediately");  // DEBUG
        // Report is already available, show it immediately
        setMode("report");
        return;
      }
      
      console.log("❌ Cache miss, starting polling");  // DEBUG
      
      // 2. Poll for the final report every 5 seconds
      const pollReport = async () => {
        try {
          const reportRes = await fetch(`${API_BASE_URL}/api/report/${newSessionId}`);
          if (reportRes.ok) {
            // Document is ready
            setMode("report");
          } else {
            // Still aggregating, wait and try again
            setTimeout(pollReport, 5000);
          }
        } catch {
          setTimeout(pollReport, 5000);
        }
      };
      
      // kick off polling
      setTimeout(pollReport, 5000);

    } catch (e) {
      console.error(e);
      setMode("search");
    }
  };

  return (
    <div className="flex flex-col relative min-h-[calc(100vh-8rem)] justify-center">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl -z-10 mix-blend-screen pointer-events-none" />

      <AnimatePresence mode="wait">
        {mode === "search" && (
          <motion.div
            key="search"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.05 }}
            transition={{ duration: 0.3 }}
            className="w-full"
          >
            <SearchForm onSearch={handleSearch} />
          </motion.div>
        )}

        {mode === "researching" && (
          <motion.div
            key="researching"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full text-center"
          >
            <div className="max-w-xl mx-auto">
              <h2 className="text-2xl font-semibold mb-4 text-zinc-200">
                Orchestrating Research on <span className="text-indigo-400">{molecule}</span>
              </h2>
              <ProgressViewer sessionId={sessionId!} />
              <div className="animate-pulse text-zinc-500 mt-8">
                Simulation running via LangGraph Agents...
              </div>
            </div>
          </motion.div>
        )}

        {mode === "report" && (
          <motion.div
            key="report"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="w-full"
          >
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-bold text-zinc-100">Repurposing Strategy</h2>
              <button 
                onClick={() => setMode("search")}
                className="text-sm px-4 py-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition"
              >
                ← New Investigation
              </button>
            </div>
            <ReportViewer sessionId={sessionId!} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
