"use client";

import { motion } from "framer-motion";
import { Activity, Database, FileSearch, TrendingUp, Sparkles, ArrowRight, CheckCircle2, Zap } from "lucide-react";

export default function AgentsPage() {
  return (
    <div className="max-w-7xl mx-auto py-12">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <h1 className="text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
          Multi-Agent Intelligence System
        </h1>
        <p className="text-xl text-zinc-400 max-w-3xl mx-auto">
          Four specialized AI agents working in parallel to analyze drug repurposing opportunities across clinical, patent, market, and regulatory domains.
        </p>
      </motion.div>

      {/* Workflow Diagram */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-20"
      >
        <h2 className="text-3xl font-bold mb-8 text-center">Agentic Workflow</h2>
        <div className="bg-gradient-to-br from-zinc-900/90 to-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-3xl p-10 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[700px] gap-2">

            {/* Step 1: User Input */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-zinc-800 flex items-center justify-center border-2 border-zinc-600 shadow-lg mb-3">
                <svg className="w-9 h-9 text-zinc-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <span className="text-sm font-semibold text-zinc-200">User Input</span>
              <span className="text-xs text-zinc-500 mt-1 text-center w-24">Molecule name</span>
            </div>

            {/* Connector */}
            <div className="flex-1 flex items-center gap-1 pb-8">
              <div className="flex-1 h-px bg-gradient-to-r from-zinc-600 to-purple-500/50"></div>
              <ArrowRight className="w-5 h-5 text-purple-400 flex-shrink-0" />
            </div>

            {/* Step 2: Planner */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500/20 to-purple-700/20 flex items-center justify-center border-2 border-purple-500/50 shadow-lg shadow-purple-500/20 mb-3">
                <Zap className="w-9 h-9 text-purple-400" />
              </div>
              <span className="text-sm font-semibold text-purple-300">Planner</span>
              <span className="text-xs text-zinc-500 mt-1 text-center w-24">ChEMBL identity resolution</span>
            </div>

            {/* Connector */}
            <div className="flex-1 flex items-center gap-1 pb-8">
              <div className="flex-1 h-px bg-gradient-to-r from-purple-500/50 to-indigo-500/50"></div>
              <ArrowRight className="w-5 h-5 text-indigo-400 flex-shrink-0" />
            </div>

            {/* Step 3: 4 Agents */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="grid grid-cols-2 gap-2 mb-3">
                {[
                  { icon: Activity, color: "blue", label: "Clinical" },
                  { icon: FileSearch, color: "amber", label: "Patent" },
                  { icon: TrendingUp, color: "green", label: "Market" },
                  { icon: Database, color: "red", label: "Regulatory" },
                ].map(({ icon: Icon, color, label }) => (
                  <div key={label} className={`w-16 h-16 rounded-xl bg-${color}-500/10 flex flex-col items-center justify-center border border-${color}-500/40 gap-1`}>
                    <Icon className={`w-6 h-6 text-${color}-400`} />
                    <span className={`text-[9px] font-medium text-${color}-300`}>{label}</span>
                  </div>
                ))}
              </div>
              <span className="text-sm font-semibold text-indigo-300">4 Agents</span>
              <span className="text-xs text-zinc-500 mt-1 text-center w-28">Running in parallel</span>
            </div>

            {/* Connector */}
            <div className="flex-1 flex items-center gap-1 pb-8">
              <div className="flex-1 h-px bg-gradient-to-r from-indigo-500/50 to-pink-500/50"></div>
              <ArrowRight className="w-5 h-5 text-pink-400 flex-shrink-0" />
            </div>

            {/* Step 4: Synthesis */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-pink-500/20 flex items-center justify-center border-2 border-indigo-500/50 shadow-lg shadow-indigo-500/20 mb-3">
                <Sparkles className="w-9 h-9 text-indigo-400" />
              </div>
              <span className="text-sm font-semibold text-indigo-300">Synthesis</span>
              <span className="text-xs text-zinc-500 mt-1 text-center w-24">Cross-domain report</span>
            </div>

            {/* Connector */}
            <div className="flex-1 flex items-center gap-1 pb-8">
              <div className="flex-1 h-px bg-gradient-to-r from-pink-500/50 to-emerald-500/50"></div>
              <ArrowRight className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            </div>

            {/* Step 5: Report */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-green-600/20 flex items-center justify-center border-2 border-emerald-500/50 shadow-lg shadow-emerald-500/20 mb-3">
                <CheckCircle2 className="w-9 h-9 text-emerald-400" />
              </div>
              <span className="text-sm font-semibold text-emerald-300">Report</span>
              <span className="text-xs text-zinc-500 mt-1 text-center w-24">Repurposing strategy</span>
            </div>

          </div>

          {/* Footer note */}
          <div className="mt-8 pt-6 border-t border-zinc-800/50 flex items-center justify-center gap-6 text-sm text-zinc-500">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></div>
              <span>Completes in <span className="text-emerald-400 font-medium">30–40 seconds</span></span>
            </div>
            <span className="text-zinc-700">•</span>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-indigo-400" />
              <span>Powered by <span className="text-indigo-400 font-medium">LangGraph</span></span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Agent Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-20"
      >
        <h2 className="text-3xl font-bold mb-8 text-center">Specialized Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {agents.map((agent, i) => (
            <AgentCard key={agent.id} agent={agent} delay={i * 0.1} />
          ))}
        </div>
      </motion.div>

      {/* Data Sources */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-3xl font-bold mb-8 text-center">Data Sources & APIs</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dataSources.map((source, i) => (
            <DataSourceCard key={source.name} source={source} delay={i * 0.05} />
          ))}
        </div>
      </motion.div>

      {/* Technical Stack */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-20"
      >
        <h2 className="text-3xl font-bold mb-8 text-center">Technical Architecture</h2>
        <div className="bg-gradient-to-br from-zinc-900/90 to-zinc-900/50 backdrop-blur-xl border border-zinc-800 rounded-3xl p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="font-semibold text-indigo-400 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                Orchestration
              </h3>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li>• LangGraph for agent coordination</li>
                <li>• Async parallel execution</li>
                <li>• Real-time SSE streaming</li>
                <li>• Redis-based state management</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-purple-400 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                AI Models
              </h3>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li>• Gemini 2.5 Flash (primary)</li>
                <li>• Nemotron 70B (fallback)</li>
                <li>• Gemini 2.5 Pro (last resort)</li>
                <li>• Rotating API keys for rate limits</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-pink-400 mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5" />
                Data Layer
              </h3>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li>• Qdrant vector database</li>
                <li>• Supabase PostgreSQL</li>
                <li>• Upstash Redis cache</li>
                <li>• Semantic chunking & embeddings</li>
              </ul>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function AgentCard({ agent, delay }: { agent: typeof agents[0]; delay: number }) {
  const Icon = agent.icon;
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className={`p-6 rounded-2xl border ${agent.borderColor} ${agent.bgColor} backdrop-blur-xl`}
    >
      <div className="flex items-start gap-4 mb-4">
        <div className={`w-14 h-14 rounded-xl ${agent.iconBg} flex items-center justify-center border ${agent.borderColor}`}>
          <Icon className={`w-7 h-7 ${agent.iconColor}`} />
        </div>
        <div className="flex-1">
          <h3 className={`text-xl font-semibold mb-1 ${agent.textColor}`}>{agent.name}</h3>
          <p className="text-sm text-zinc-500">{agent.description}</p>
        </div>
      </div>
      <div className="space-y-3">
        <div>
          <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-2">Key Tasks</h4>
          <ul className="space-y-1">
            {agent.tasks.map((task, i) => (
              <li key={i} className="text-sm text-zinc-400 flex items-start gap-2">
                <span className={`mt-1.5 w-1 h-1 rounded-full ${agent.dotColor}`}></span>
                <span>{task}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wide mb-2">Data Sources</h4>
          <div className="flex flex-wrap gap-2">
            {agent.sources.map((source, i) => (
              <span key={i} className="text-xs px-2 py-1 rounded-md bg-zinc-800/50 text-zinc-400 border border-zinc-700/50">
                {source}
              </span>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function DataSourceCard({ source, delay }: { source: typeof dataSources[0]; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay }}
      className="p-4 rounded-xl bg-zinc-900/50 border border-zinc-800 hover:border-zinc-700 transition-colors"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-zinc-200">{source.name}</h3>
        {source.free && (
          <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            Free
          </span>
        )}
      </div>
      <p className="text-sm text-zinc-500 mb-3">{source.description}</p>
      <div className="flex items-center gap-2">
        <span className={`text-xs px-2 py-1 rounded-md ${source.categoryBg} ${source.categoryText}`}>
          {source.category}
        </span>
        {source.url && (
          <a 
            href={source.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs text-indigo-400 hover:text-indigo-300 transition"
          >
            View API →
          </a>
        )}
      </div>
    </motion.div>
  );
}

const agents = [
  {
    id: "clinical",
    name: "Clinical Evidence Agent",
    description: "Analyzes clinical trials and research data",
    icon: Activity,
    bgColor: "bg-blue-500/5",
    borderColor: "border-blue-500/30",
    iconBg: "bg-blue-500/10",
    iconColor: "text-blue-400",
    textColor: "text-blue-300",
    dotColor: "bg-blue-400",
    tasks: [
      "Search ClinicalTrials.gov for relevant studies",
      "Extract trial phases, indications, and outcomes",
      "Identify repurposing signals from Phase 2+ trials",
      "Assess clinical precedent and evidence strength"
    ],
    sources: ["ClinicalTrials.gov", "PubMed", "ChEMBL"]
  },
  {
    id: "patent",
    name: "Patent Landscape Agent",
    description: "Reviews patent filings and FTO status",
    icon: FileSearch,
    bgColor: "bg-amber-500/5",
    borderColor: "border-amber-500/30",
    iconBg: "bg-amber-500/10",
    iconColor: "text-amber-400",
    textColor: "text-amber-300",
    dotColor: "bg-amber-400",
    tasks: [
      "Search EPO Open Patent Services",
      "Analyze patent claims and expiration dates",
      "Calculate Freedom-to-Operate (FTO) score",
      "Identify patent barriers and opportunities"
    ],
    sources: ["EPO OPS", "USPTO", "Patent databases"]
  },
  {
    id: "market",
    name: "Market Analysis Agent",
    description: "Evaluates market potential and competition",
    icon: TrendingUp,
    bgColor: "bg-green-500/5",
    borderColor: "border-green-500/30",
    iconBg: "bg-green-500/10",
    iconColor: "text-green-400",
    textColor: "text-green-300",
    dotColor: "bg-green-400",
    tasks: [
      "Assess target indication market size",
      "Analyze competitive landscape",
      "Evaluate commercial potential",
      "Identify market entry barriers"
    ],
    sources: ["WHO GHO", "Market databases", "PubChem"]
  },
  {
    id: "regulatory",
    name: "Regulatory Pathway Agent",
    description: "Assesses regulatory requirements and history",
    icon: Database,
    bgColor: "bg-red-500/5",
    borderColor: "border-red-500/30",
    iconBg: "bg-red-500/10",
    iconColor: "text-red-400",
    textColor: "text-red-300",
    dotColor: "bg-red-400",
    tasks: [
      "Review FDA approval history",
      "Analyze drug labels and safety data",
      "Assess regulatory complexity",
      "Identify approval pathway options"
    ],
    sources: ["OpenFDA", "DailyMed", "FDA databases"]
  }
];

const dataSources = [
  {
    name: "ClinicalTrials.gov",
    description: "Clinical trial registry with 400k+ studies",
    category: "Clinical",
    categoryBg: "bg-blue-500/10",
    categoryText: "text-blue-400",
    free: true,
    url: "https://clinicaltrials.gov/api/v2"
  },
  {
    name: "ChEMBL",
    description: "Bioactive molecules database from EMBL-EBI",
    category: "Clinical",
    categoryBg: "bg-blue-500/10",
    categoryText: "text-blue-400",
    free: true,
    url: "https://www.ebi.ac.uk/chembl/api/data"
  },
  {
    name: "EPO OPS",
    description: "European Patent Office Open Patent Services",
    category: "Patent",
    categoryBg: "bg-amber-500/10",
    categoryText: "text-amber-400",
    free: true,
    url: "https://www.epo.org/searching-for-patents/data/web-services/ops.html"
  },
  {
    name: "OpenFDA",
    description: "FDA drug labels, adverse events, and recalls",
    category: "Regulatory",
    categoryBg: "bg-red-500/10",
    categoryText: "text-red-400",
    free: true,
    url: "https://open.fda.gov"
  },
  {
    name: "WHO GHO",
    description: "World Health Organization Global Health Observatory",
    category: "Market",
    categoryBg: "bg-green-500/10",
    categoryText: "text-green-400",
    free: true,
    url: "https://www.who.int/data/gho"
  },
  {
    name: "PubMed",
    description: "30M+ biomedical literature citations",
    category: "Clinical",
    categoryBg: "bg-blue-500/10",
    categoryText: "text-blue-400",
    free: true,
    url: "https://www.ncbi.nlm.nih.gov/home/develop/api/"
  },
  {
    name: "PubChem",
    description: "Chemical molecules and biological activities",
    category: "Market",
    categoryBg: "bg-green-500/10",
    categoryText: "text-green-400",
    free: true,
    url: "https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest"
  },
  {
    name: "DailyMed",
    description: "FDA-published drug labeling information",
    category: "Regulatory",
    categoryBg: "bg-red-500/10",
    categoryText: "text-red-400",
    free: true,
    url: "https://dailymed.nlm.nih.gov/dailymed/app-support-web-services.cfm"
  },
  {
    name: "Open Targets",
    description: "Target-disease associations and drug data",
    category: "Clinical",
    categoryBg: "bg-blue-500/10",
    categoryText: "text-blue-400",
    free: true,
    url: "https://platform.opentargets.org"
  }
];
