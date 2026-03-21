"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, CircleDashed, Loader2, XCircle, Activity, Database, FileSearch, Sparkles, TrendingUp } from "lucide-react";
import { useSSE } from "@/hooks/useSSE";
import { useState, useEffect } from "react";

const domains = [
  { 
    id: "clinical", 
    title: "Clinical Evidence", 
    icon: Activity,
    color: "blue",
    description: "Analyzing clinical trials and research data"
  },
  { 
    id: "patent", 
    title: "Patent Landscape", 
    icon: FileSearch,
    color: "amber",
    description: "Reviewing patent filings and FTO status"
  },
  { 
    id: "market", 
    title: "Market Analysis", 
    icon: TrendingUp,
    color: "green",
    description: "Evaluating market potential and competition"
  },
  { 
    id: "regulatory", 
    title: "Regulatory Pathway", 
    icon: Database,
    color: "red",
    description: "Assessing regulatory requirements and history"
  }
];

const colorClasses = {
  purple: {
    bg: "bg-purple-500/10",
    border: "border-purple-500/30",
    text: "text-purple-300",
    icon: "text-purple-400",
    glow: "shadow-purple-500/20"
  },
  blue: {
    bg: "bg-blue-500/10",
    border: "border-blue-500/30",
    text: "text-blue-300",
    icon: "text-blue-400",
    glow: "shadow-blue-500/20"
  },
  amber: {
    bg: "bg-amber-500/10",
    border: "border-amber-500/30",
    text: "text-amber-300",
    icon: "text-amber-400",
    glow: "shadow-amber-500/20"
  },
  green: {
    bg: "bg-green-500/10",
    border: "border-green-500/30",
    text: "text-green-300",
    icon: "text-green-400",
    glow: "shadow-green-500/20"
  },
  red: {
    bg: "bg-red-500/10",
    border: "border-red-500/30",
    text: "text-red-300",
    icon: "text-red-400",
    glow: "shadow-red-500/20"
  }
};

export default function ProgressViewer({ sessionId, onComplete }: { sessionId: string; onComplete?: () => void }) {
  const { events, isDone } = useSSE(sessionId, onComplete);
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
    
    if (isDone) {
      clearInterval(interval);
    }
    
    return () => clearInterval(interval);
  }, [isDone]);

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
      message: completed?.message || started?.message || "",
      startTime: started?.timestamp,
      endTime: completed?.timestamp || failed?.timestamp
    };
  });

  const completedCount = domainStatus.filter(d => d.completed).length;
  const failedCount = domainStatus.filter(d => d.failed).length;
  const activeCount = domainStatus.filter(d => d.started && !d.completed && !d.failed).length;
  const progressPercent = isDone ? 100 : (completedCount / domains.length) * 100;

  // Get synthesis status
  const synthesisStarted = events.find(e => e.event === "synthesis_started");
  const synthesisComplete = events.find(e => e.event === "synthesis_complete");

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Main Progress Card */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-br from-zinc-900/90 to-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-3xl p-8 shadow-2xl relative overflow-hidden"
      >
        {/* Animated background gradient */}
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 via-purple-500/5 to-pink-500/5 animate-pulse"></div>
        
        {/* Progress bar */}
        <div className="absolute top-0 left-0 w-full h-1.5 bg-zinc-800/50">
          <motion.div 
            className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"
            initial={{ width: "0%" }}
            animate={{ width: `${progressPercent}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-indigo-500/30 shadow-lg shadow-indigo-500/20">
                {isDone ? (
                  <CheckCircle2 className="w-8 h-8 text-indigo-400" />
                ) : (
                  <Loader2 className="w-8 h-8 text-indigo-400 animate-spin" />
                )}
              </div>
              <div>
                <h3 className="text-2xl font-bold text-zinc-100 mb-1">
                  {isDone ? "Analysis Complete!" : "Multi-Agent Research in Progress"}
                </h3>
                <p className="text-sm text-zinc-400">
                  {isDone 
                    ? `Completed in ${formatTime(elapsedTime)}`
                    : `${completedCount} of ${domains.length} agents completed • ${formatTime(elapsedTime)} elapsed`
                  }
                </p>
              </div>
            </div>
            
            {/* Stats */}
            <div className="flex gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-400">{completedCount}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wide">Complete</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">{activeCount}</div>
                <div className="text-xs text-zinc-500 uppercase tracking-wide">Active</div>
              </div>
              {failedCount > 0 && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-400">{failedCount}</div>
                  <div className="text-xs text-zinc-500 uppercase tracking-wide">Failed</div>
                </div>
              )}
            </div>
          </div>

          {/* Agent Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {domainStatus.map((domain, i) => {
              const colors = colorClasses[domain.color as keyof typeof colorClasses];
              const Icon = domain.icon;
              
              return (
                <motion.div 
                  key={domain.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className={`relative p-5 rounded-2xl border transition-all duration-300 ${
                    domain.completed 
                      ? `${colors.bg} ${colors.border} ${colors.glow} shadow-lg` 
                      : domain.failed
                      ? 'bg-red-500/10 border-red-500/30'
                      : domain.started
                      ? 'bg-zinc-800/50 border-zinc-700 shadow-md'
                      : 'bg-zinc-800/20 border-zinc-800'
                  }`}
                >
                  {/* Status indicator dot */}
                  <div className="absolute top-3 right-3">
                    {domain.completed ? (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", bounce: 0.5 }}
                      >
                        <CheckCircle2 className={`w-6 h-6 ${colors.icon}`} />
                      </motion.div>
                    ) : domain.failed ? (
                      <XCircle className="w-6 h-6 text-red-400" />
                    ) : domain.started ? (
                      <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
                    ) : (
                      <CircleDashed className="w-6 h-6 text-zinc-600" />
                    )}
                  </div>

                  <div className="flex items-start gap-3 mb-3">
                    <div className={`w-10 h-10 rounded-xl ${colors.bg} flex items-center justify-center border ${colors.border}`}>
                      <Icon className={`w-5 h-5 ${colors.icon}`} />
                    </div>
                    <div className="flex-1">
                      <h4 className={`font-semibold mb-1 ${
                        domain.completed || domain.started ? colors.text : 'text-zinc-500'
                      }`}>
                        {domain.title}
                      </h4>
                      <p className="text-xs text-zinc-500 leading-relaxed">
                        {domain.description}
                      </p>
                    </div>
                  </div>

                  {/* Message */}
                  {domain.message && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      className="mt-3 pt-3 border-t border-zinc-700/50"
                    >
                      <p className="text-xs text-zinc-400 leading-relaxed">
                        {domain.message}
                      </p>
                    </motion.div>
                  )}
                </motion.div>
              );
            })}
          </div>

          {/* Synthesis Phase */}
          <AnimatePresence>
            {synthesisStarted && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`p-5 rounded-2xl border ${
                  synthesisComplete
                    ? 'bg-indigo-500/10 border-indigo-500/30 shadow-lg shadow-indigo-500/20'
                    : 'bg-purple-500/10 border-purple-500/30'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center border border-indigo-500/30">
                    {synthesisComplete ? (
                      <CheckCircle2 className="w-5 h-5 text-indigo-400" />
                    ) : (
                      <Sparkles className="w-5 h-5 text-purple-400 animate-pulse" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-indigo-300 mb-1">
                      {synthesisComplete ? "Synthesis Complete" : "Cross-Domain Synthesis"}
                    </h4>
                    <p className="text-xs text-zinc-400">
                      {synthesisComplete 
                        ? "Report generated with opportunity scoring and strategic recommendations"
                        : "Integrating findings across all domains..."
                      }
                    </p>
                  </div>
                  {!synthesisComplete && (
                    <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Event Log */}
      {events.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-2xl p-6"
        >
          <h4 className="text-sm font-semibold text-zinc-400 uppercase tracking-wide mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Activity Log
          </h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {events.slice(-10).reverse().map((event, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-start gap-3 text-xs p-2 rounded-lg hover:bg-zinc-800/30 transition-colors"
              >
                <span className="text-zinc-600 font-mono shrink-0">
                  {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : '--:--:--'}
                </span>
                <span className="text-zinc-500 shrink-0 capitalize">[{event.domain}]</span>
                <span className="text-zinc-400 flex-1">{event.message}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}
