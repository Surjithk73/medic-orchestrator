"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Zap } from "lucide-react";

interface RepurposingOpportunity {
  target_indication: string;
  opportunity_score: number;
  rationale: string;
  patent_barrier: string;
  clinical_precedent: string;
}

interface Report {
  executive_summary?: string;
  opportunities?: RepurposingOpportunity[];
  data_gaps?: string[];
}

export default function ReportViewer({ sessionId }: { sessionId: string }) {
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/api/report/${sessionId}`)
      .then(res => res.json())
      .then(data => setReport(data))
      .catch(console.error);
  }, [sessionId]);

  if (!report) {
    return <div className="text-zinc-500 animate-pulse">Loading definitive strategy report...</div>;
  }

  // Backend FinalReportSchema uses `opportunities` (list of RepurposingOpportunity)
  const opportunities = report.opportunities || [];
  const gaps = report.data_gaps || [];

  return (
    <div className="w-full max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Sidebar Overview */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="col-span-1 space-y-6"
      >
        <div className="p-6 bg-zinc-900/80 border border-zinc-800 rounded-3xl">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center mb-4 shadow-[0_0_20px_rgba(52,211,153,0.3)]">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-xl font-bold text-zinc-100 mb-2">Executive Summary</h3>
          <p className="text-sm text-zinc-400 leading-relaxed">
            {report.executive_summary || "Synthesis engine did not yield an executive summary."}
          </p>
        </div>

        <div className="p-6 border border-zinc-800 rounded-3xl">
          <h3 className="text-sm font-bold text-zinc-500 mb-4 uppercase tracking-wider">Data Gaps & Risks</h3>
          <ul className="space-y-3">
            {gaps.length > 0 ? gaps.map((gap: string, i: number) => (
              <li key={i} className="flex gap-3 text-sm text-zinc-300 items-start">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5 shrink-0" />
                {gap}
              </li>
            )) : (
              <li className="text-sm text-zinc-500">No significant data gaps identified.</li>
            )}
          </ul>
        </div>
      </motion.div>

      {/* Main Opportunities */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="col-span-1 md:col-span-2 space-y-6"
      >
        <h3 className="text-2xl font-semibold text-zinc-100 flex items-center gap-2">
          Top Identified Opportunities
        </h3>
        
        {opportunities.map((op: RepurposingOpportunity, index: number) => {
          const colorClass = index % 2 === 0 ? "indigo" : "purple";
          return (
            <div key={index} className={`group relative bg-[#0a0a0b] border border-zinc-800 hover:border-${colorClass}-500/50 rounded-3xl p-6 transition-all duration-300`}>
              <div className={`absolute top-6 right-6 flex items-center justify-center w-12 h-12 rounded-full border border-${colorClass}-500/20 bg-${colorClass}-500/10`}>
                <span className={`text-${colorClass}-400 font-bold text-lg`}>{op.opportunity_score}</span>
              </div>
              <h4 className="text-xl font-bold text-zinc-100 mb-1">{op.target_indication}</h4>
              <p className={`text-sm text-${colorClass}-400 font-medium mb-6`}>Potential Application</p>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="block text-zinc-500 mb-1">Biological Rationale</span>
                  <p className="text-zinc-300">{op.rationale}</p>
                </div>
                <div>
                  <span className="block text-zinc-500 mb-1">Patent / Clinical Status</span>
                  <p className="text-zinc-300">{op.patent_barrier} | {op.clinical_precedent}</p>
                </div>
              </div>
            </div>
          );
        })}
      </motion.div>
    </div>
  );
}
