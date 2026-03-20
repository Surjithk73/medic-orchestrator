"use client";

import { motion } from "framer-motion";
import { CheckCircle2, CircleDashed, Loader2, XCircle } from "lucide-react";
import { useSSE } from "@/hooks/useSSE";

const domains = [
  { id: "clinical", title: "Clinical Viability" },
  { id: "patent", title: "Patent & FTO" },
  { id: "market", title: "Market Need" },
  { id: "regulatory", title: "Regulatory Pathway" }
];

export default function ProgressViewer({ sessionId }: { sessionId: string }) {
  const { events, isDone } = useSSE(sessionId);

  // Track which domains have started and completed
  const domainStatus = domains.map(d => {
    const started = events.find(e => e.domain === d.id && e.status === "started");
    const completed = events.find(e => e.domain === d.id && e.status === "completed");
    const failed = events.find(e => e.domain === d.id && e.status === "failed");
    
    return {
      ...d,
      started: !!started,
      completed: !!completed,
      failed: !!failed,
      message: completed?.message || started?.message || ""
    };
  });

  const completedCount = domainStatus.filter(d => d.completed).length;
  const progressPercent = isDone ? 100 : (completedCount / domains.length) * 100;

  return (
    <div className="w-full max-w-lg mx-auto bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-1 bg-zinc-800">
        <motion.div 
          className="h-full bg-gradient-to-r from-indigo-500 to-cyan-400"
          initial={{ width: "0%" }}
          animate={{ width: `${progressPercent}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      <div className="flex items-center gap-4 mb-8">
        <div className="w-12 h-12 rounded-2xl bg-indigo-500/20 flex items-center justify-center border border-indigo-500/30">
          {isDone ? (
            <CheckCircle2 className="w-6 h-6 text-indigo-400" />
          ) : (
            <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
          )}
        </div>
        <div className="text-left">
          <h3 className="text-lg font-semibold text-zinc-100">
            {isDone ? "Analysis Complete" : "DeepSeek & Gemini Agents"}
          </h3>
          <p className="text-sm text-zinc-400">
            {isDone ? "Report ready for review" : "orchestrating parallel literature scans..."}
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {domainStatus.map((domain, i) => {
          return (
            <motion.div 
              key={domain.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className={`flex items-center justify-between p-4 rounded-xl border ${
                domain.completed 
                  ? 'bg-indigo-500/10 border-indigo-500/30' 
                  : domain.failed
                  ? 'bg-red-500/10 border-red-500/30'
                  : domain.started
                  ? 'bg-zinc-800/40 border-zinc-700'
                  : 'bg-zinc-800/20 border-zinc-800'
              }`}
            >
              <div className="flex-1">
                <span className={`font-medium block ${
                  domain.completed 
                    ? 'text-indigo-300' 
                    : domain.failed
                    ? 'text-red-300'
                    : domain.started
                    ? 'text-zinc-300'
                    : 'text-zinc-500'
                }`}>
                  {domain.title}
                </span>
                {domain.message && (
                  <span className="text-xs text-zinc-500 mt-1 block">
                    {domain.message}
                  </span>
                )}
              </div>
              {domain.completed ? (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", bounce: 0.5 }}
                >
                  <CheckCircle2 className="w-5 h-5 text-indigo-400" />
                </motion.div>
              ) : domain.failed ? (
                <XCircle className="w-5 h-5 text-red-400" />
              ) : domain.started ? (
                <Loader2 className="w-5 h-5 text-zinc-400 animate-spin" />
              ) : (
                <CircleDashed className="w-5 h-5 text-zinc-600" />
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
