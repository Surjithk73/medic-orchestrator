"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, ExternalLink, Calendar, FileText } from "lucide-react";

interface Citation {
  id: string;
  domain: string;
  url: string;
  title: string;
  source_section?: string;
  retrieved_at?: string;
  confidence?: number;
}

interface CitationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  citation: Citation | null;
}

export default function CitationDrawer({ isOpen, onClose, citation }: CitationDrawerProps) {
  if (!citation) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-full max-w-2xl bg-zinc-900 border-l border-zinc-800 shadow-2xl z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-zinc-900/95 backdrop-blur-xl border-b border-zinc-800 p-6 z-10">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-semibold uppercase border border-indigo-500/30">
                      {citation.domain}
                    </span>
                    {citation.confidence && (
                      <span className="text-xs text-zinc-500">
                        Confidence: {(citation.confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                  <h2 className="text-xl font-bold text-zinc-100 leading-tight">
                    Citation Details
                  </h2>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg hover:bg-zinc-800 transition-colors text-zinc-400 hover:text-zinc-100"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Title */}
              <div>
                <div className="flex items-center gap-2 text-zinc-500 text-sm mb-2">
                  <FileText className="w-4 h-4" />
                  <span className="font-semibold uppercase tracking-wide">Source Title</span>
                </div>
                <p className="text-zinc-200 text-lg font-medium leading-relaxed">
                  {citation.title}
                </p>
              </div>

              {/* Section */}
              {citation.source_section && (
                <div>
                  <div className="flex items-center gap-2 text-zinc-500 text-sm mb-2">
                    <FileText className="w-4 h-4" />
                    <span className="font-semibold uppercase tracking-wide">Section</span>
                  </div>
                  <p className="text-zinc-300 leading-relaxed">
                    {citation.source_section}
                  </p>
                </div>
              )}

              {/* URL */}
              <div>
                <div className="flex items-center gap-2 text-zinc-500 text-sm mb-2">
                  <ExternalLink className="w-4 h-4" />
                  <span className="font-semibold uppercase tracking-wide">Source URL</span>
                </div>
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition-colors text-sm font-medium"
                >
                  <span>Open Source</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
                <p className="mt-2 text-xs text-zinc-500 break-all">
                  {citation.url}
                </p>
              </div>

              {/* Retrieved At */}
              {citation.retrieved_at && (
                <div>
                  <div className="flex items-center gap-2 text-zinc-500 text-sm mb-2">
                    <Calendar className="w-4 h-4" />
                    <span className="font-semibold uppercase tracking-wide">Retrieved</span>
                  </div>
                  <p className="text-zinc-300">
                    {new Date(citation.retrieved_at).toLocaleString()}
                  </p>
                </div>
              )}

              {/* Metadata Card */}
              <div className="rounded-xl bg-zinc-800/50 border border-zinc-700 p-4">
                <h4 className="text-sm font-semibold text-zinc-400 mb-3 uppercase tracking-wide">
                  Citation Metadata
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Domain:</span>
                    <span className="text-zinc-300 font-medium">{citation.domain}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-zinc-500">Citation ID:</span>
                    <span className="text-zinc-300 font-mono text-xs">{citation.id}</span>
                  </div>
                  {citation.confidence && (
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Confidence Score:</span>
                      <span className="text-zinc-300 font-medium">
                        {(citation.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
