"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Sparkles, TrendingUp, AlertTriangle, FileText, Beaker, Scale, Building2 } from "lucide-react";
import { API_BASE_URL } from "@/lib/config";

interface RepurposingOpportunity {
  target_indication: string;
  opportunity_score: number;
  rationale: string;
  patent_barrier: string;
  clinical_precedent: string;
}

interface Report {
  executive_summary?: string;
  mechanism_of_action?: string;
  opportunities?: RepurposingOpportunity[];
  data_gaps?: string[];
}

export default function ReportViewer({ sessionId }: { sessionId: string }) {
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/report/${sessionId}`)
      .then(res => res.json())
      .then(data => setReport(data))
      .catch(console.error);
  }, [sessionId]);

  if (!report) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-zinc-400">Loading comprehensive analysis...</p>
        </div>
      </div>
    );
  }

  const opportunities = report.opportunities || [];
  const gaps = report.data_gaps || [];

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 0.7) return "from-emerald-500 to-green-500";
    if (score >= 0.5) return "from-yellow-500 to-orange-500";
    return "from-orange-500 to-red-500";
  };

  const getScoreBadge = (score: number) => {
    if (score >= 0.7) return { text: "High Potential", color: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" };
    if (score >= 0.5) return { text: "Moderate", color: "bg-yellow-500/10 text-yellow-400 border-yellow-500/30" };
    return { text: "Low Potential", color: "bg-orange-500/10 text-orange-400 border-orange-500/30" };
  };

  return (
    <div className="w-full max-w-7xl mx-auto space-y-8">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-500/10 via-purple-500/10 to-pink-500/10 border border-indigo-500/20 p-8"
      >
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/50">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-zinc-100">Executive Summary</h2>
              <p className="text-sm text-zinc-400">AI-Generated Strategic Analysis</p>
            </div>
          </div>
          <p className="text-zinc-300 leading-relaxed text-lg">
            {report.executive_summary || "Comprehensive analysis completed. Review opportunities below."}
          </p>
        </div>
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>
      </motion.div>

      {/* Mechanism of Action */}
      {report.mechanism_of_action && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl bg-zinc-900/50 border border-zinc-800 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <Beaker className="w-5 h-5 text-cyan-400" />
            <h3 className="text-lg font-semibold text-zinc-100">Mechanism of Action</h3>
          </div>
          <p className="text-zinc-400 leading-relaxed">{report.mechanism_of_action}</p>
        </motion.div>
      )}

      {/* Opportunities Grid */}
      <div>
        <div className="flex items-center gap-3 mb-6">
          <TrendingUp className="w-6 h-6 text-indigo-400" />
          <h3 className="text-2xl font-bold text-zinc-100">Repurposing Opportunities</h3>
          <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-sm font-medium border border-indigo-500/30">
            {opportunities.length} {opportunities.length === 1 ? 'Opportunity' : 'Opportunities'} Identified
          </span>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {opportunities.map((op: RepurposingOpportunity, index: number) => {
            const badge = getScoreBadge(op.opportunity_score);
            
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
                className="group relative bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-indigo-500/5"
              >
                {/* Score Badge */}
                <div className="absolute top-6 right-6">
                  <div className={`px-4 py-2 rounded-xl border ${badge.color} font-semibold text-sm`}>
                    {badge.text}
                  </div>
                </div>

                {/* Title */}
                <div className="mb-6 pr-32">
                  <h4 className="text-2xl font-bold text-zinc-100 mb-2">{op.target_indication}</h4>
                  <div className="flex items-center gap-2">
                    <div className={`w-16 h-2 rounded-full bg-gradient-to-r ${getScoreColor(op.opportunity_score)}`}></div>
                    <span className="text-sm font-medium text-zinc-400">Score: {op.opportunity_score.toFixed(2)}</span>
                  </div>
                </div>

                {/* Content Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Rationale */}
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-zinc-400">
                      <FileText className="w-4 h-4" />
                      <span className="text-sm font-semibold uppercase tracking-wide">Biological Rationale</span>
                    </div>
                    <p className="text-zinc-300 leading-relaxed">{op.rationale}</p>
                  </div>

                  {/* Clinical & Patent */}
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-zinc-400">
                        <Building2 className="w-4 h-4" />
                        <span className="text-sm font-semibold uppercase tracking-wide">Clinical Precedent</span>
                      </div>
                      <p className="text-zinc-300 leading-relaxed">{op.clinical_precedent}</p>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-zinc-400">
                        <Scale className="w-4 h-4" />
                        <span className="text-sm font-semibold uppercase tracking-wide">Patent Barrier</span>
                      </div>
                      <p className="text-zinc-300 leading-relaxed">{op.patent_barrier}</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Data Gaps */}
      {gaps.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="rounded-2xl bg-orange-500/5 border border-orange-500/20 p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-orange-400" />
            <h3 className="text-lg font-semibold text-zinc-100">Data Gaps & Limitations</h3>
          </div>
          <ul className="space-y-3">
            {gaps.map((gap: string, i: number) => (
              <li key={i} className="flex gap-3 items-start">
                <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2 shrink-0" />
                <span className="text-zinc-400 leading-relaxed">{gap}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}
    </div>
  );
}
