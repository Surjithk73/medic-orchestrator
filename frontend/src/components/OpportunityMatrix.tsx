"use client";

import { motion } from "framer-motion";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ZAxis } from 'recharts';
import { TrendingUp } from "lucide-react";

interface Opportunity {
  target_indication: string;
  opportunity_score: number;
  clinical_score?: number;
  commercial_score?: number;
  fto_score?: number;
  regulatory_score?: number;
}

interface OpportunityMatrixProps {
  opportunities: Opportunity[];
}

export default function OpportunityMatrix({ opportunities }: OpportunityMatrixProps) {
  // Transform data for scatter chart
  const chartData = opportunities.map((opp) => ({
    name: opp.target_indication,
    x: (opp.commercial_score || opp.opportunity_score) * 10, // Commercial Potential (0-10)
    y: (opp.clinical_score || opp.opportunity_score) * 10, // Clinical Evidence (0-10)
    z: (opp.fto_score || opp.opportunity_score) * 100, // Bubble size
    regulatory: opp.regulatory_score || opp.opportunity_score,
    overall: opp.opportunity_score,
  }));

  // Get color based on regulatory complexity
  const getColor = (regulatory: number) => {
    if (regulatory >= 0.7) return "#10b981"; // Green - Simple
    if (regulatory >= 0.5) return "#f59e0b"; // Amber - Moderate
    return "#ef4444"; // Red - Complex
  };

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-zinc-900 border border-zinc-700 rounded-lg p-4 shadow-xl">
          <p className="font-semibold text-zinc-100 mb-2">{data.name}</p>
          <div className="space-y-1 text-sm">
            <p className="text-zinc-400">
              Clinical Evidence: <span className="text-zinc-200 font-medium">{data.y.toFixed(1)}/10</span>
            </p>
            <p className="text-zinc-400">
              Commercial Potential: <span className="text-zinc-200 font-medium">{data.x.toFixed(1)}/10</span>
            </p>
            <p className="text-zinc-400">
              Freedom to Operate: <span className="text-zinc-200 font-medium">{(data.z / 10).toFixed(1)}/10</span>
            </p>
            <p className="text-zinc-400">
              Regulatory: <span className="text-zinc-200 font-medium">{(data.regulatory * 10).toFixed(1)}/10</span>
            </p>
            <div className="pt-2 mt-2 border-t border-zinc-700">
              <p className="text-zinc-400">
                Overall Score: <span className="text-indigo-400 font-bold">{(data.overall * 100).toFixed(0)}%</span>
              </p>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="rounded-2xl bg-zinc-900/50 border border-zinc-800 p-6"
    >
      <div className="flex items-center gap-3 mb-6">
        <TrendingUp className="w-6 h-6 text-purple-400" />
        <h3 className="text-2xl font-bold text-zinc-100">Opportunity Matrix</h3>
      </div>

      <div className="mb-4">
        <p className="text-zinc-400 text-sm mb-3">
          Visual representation of repurposing opportunities across clinical evidence and commercial potential dimensions.
        </p>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
            <span className="text-zinc-500">Simple Regulatory Path</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-amber-500"></div>
            <span className="text-zinc-500">Moderate Complexity</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-zinc-500">Complex Regulatory</span>
          </div>
        </div>
      </div>

      <div className="bg-zinc-950/50 rounded-xl p-4 border border-zinc-800/50">
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
            <XAxis
              type="number"
              dataKey="x"
              name="Commercial Potential"
              domain={[0, 10]}
              label={{
                value: 'Commercial Potential →',
                position: 'bottom',
                offset: 40,
                style: { fill: '#71717a', fontSize: 14, fontWeight: 600 }
              }}
              tick={{ fill: '#71717a' }}
              stroke="#3f3f46"
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Clinical Evidence"
              domain={[0, 10]}
              label={{
                value: '← Clinical Evidence',
                angle: -90,
                position: 'left',
                offset: 40,
                style: { fill: '#71717a', fontSize: 14, fontWeight: 600 }
              }}
              tick={{ fill: '#71717a' }}
              stroke="#3f3f46"
            />
            <ZAxis type="number" dataKey="z" range={[100, 1000]} />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Opportunities" data={chartData} fill="#8b5cf6">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.regulatory)} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="mt-4 p-4 rounded-lg bg-zinc-800/30 border border-zinc-700/50">
        <p className="text-xs text-zinc-500 leading-relaxed">
          <span className="font-semibold text-zinc-400">How to read:</span> Bubble position shows clinical evidence (Y-axis) vs commercial potential (X-axis). 
          Bubble size represents freedom-to-operate score. Color indicates regulatory pathway complexity. 
          Top-right quadrant represents highest-priority opportunities.
        </p>
      </div>
    </motion.div>
  );
}
