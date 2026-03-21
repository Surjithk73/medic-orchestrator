"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Brain, CheckCircle2, Loader2, XCircle } from "lucide-react";

interface TraceEvent {
  event: string;
  domain: string;
  status: string;
  message: string;
  timestamp?: string;
}

interface ReasoningTraceProps {
  events: TraceEvent[];
}

export default function ReasoningTrace({ events }: ReasoningTraceProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-emerald-400" />;
      case "started":
      case "running":
        return <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Brain className="w-5 h-5 text-zinc-400" />;
    }
  };

  const getDomainColor = (domain: string) => {
    const colors: Record<string, string> = {
      planner: "bg-purple-500/10 text-purple-400 border-purple-500/30",
      clinical: "bg-blue-500/10 text-blue-400 border-blue-500/30",
      patent: "bg-amber-500/10 text-amber-400 border-amber-500/30",
      market: "bg-green-500/10 text-green-400 border-green-500/30",
      regulatory: "bg-red-500/10 text-red-400 border-red-500/30",
      synthesis: "bg-indigo-500/10 text-indigo-400 border-indigo-500/30",
      system: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
    };
    return colors[domain] || colors.system;
  };

  if (events.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl bg-zinc-900/50 border border-zinc-800 overflow-hidden"
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-6 hover:bg-zinc-800/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-purple-400" />
          <div className="text-left">
            <h3 className="text-xl font-bold text-zinc-100">Agent Reasoning Trace</h3>
            <p className="text-sm text-zinc-500">
              {events.length} events • Click to {isExpanded ? "collapse" : "expand"}
            </p>
          </div>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronDown className="w-5 h-5 text-zinc-400" />
        </motion.div>
      </button>

      {/* Trace Events */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-zinc-800"
          >
            <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
              {events.map((event, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-start gap-4 p-4 rounded-lg bg-zinc-800/30 border border-zinc-700/50 hover:border-zinc-600/50 transition-colors"
                >
                  {/* Status Icon */}
                  <div className="mt-0.5">
                    {getStatusIcon(event.status)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2.5 py-1 rounded-md text-xs font-semibold uppercase border ${getDomainColor(event.domain)}`}>
                        {event.domain}
                      </span>
                      <span className="text-xs text-zinc-500">
                        {event.event.replace(/_/g, " ")}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-300 leading-relaxed">
                      {event.message}
                    </p>
                    {event.timestamp && (
                      <p className="text-xs text-zinc-600 mt-2">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
