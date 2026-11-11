import React from 'react';

interface TraceStep {
  node: string;
  action: string;
  tokens: number;
  cost_usd: number;
}

interface RunTimelineProps {
  steps: TraceStep[];
  isInterrupted: boolean;
}

export const RunTimeline: React.FC<RunTimelineProps> = ({ steps, isInterrupted }) => {
  return (
    <div className="flex flex-col gap-3 my-4">
      {steps.map((s, idx) => (
        <div key={idx} className="bg-slate-800 border-l-4 border-sky-400 p-3 rounded-r-lg text-sm">
          <div className="flex justify-between items-center">
            <span className="font-semibold text-slate-200">Node: {s.node}</span>
            <span className="text-xs text-slate-400">{s.tokens} tokens</span>
          </div>
          <p className="text-slate-400 text-xs mt-1">Action: {s.action}</p>
        </div>
      ))}
      {isInterrupted && (
        <div className="bg-amber-950/40 border-l-4 border-amber-500 p-3 rounded-r-lg text-sm text-amber-300">
          <strong>Interrupt Paused:</strong> Graph paused waiting for human approval.
        </div>
      )}
    </div>
  );
};
