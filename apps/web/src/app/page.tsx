'use client';

import React, { useEffect, useState } from 'react';
import { apiClient, JobPosting, ProposalDetail } from '../lib/api/client';
import { EvidenceHover } from '../components/EvidenceHover';
import { ApprovalPanel } from '../components/ApprovalPanel';
import { RunTimeline } from '../components/RunTimeline';

export default function GigBidDashboard() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [activeScreen, setActiveScreen] = useState('inbox');
  const [activeProposal, setActiveProposal] = useState<ProposalDetail | null>(null);
  const [timelineSteps, setTimelineSteps] = useState<any[]>([]);
  const [isInterrupted, setIsInterrupted] = useState(false);

  useEffect(() => {
    apiClient.getJobs().then(setJobs).catch(console.error);
  }, []);

  const handleRunCopilot = async (jobId: string) => {
    setActiveScreen('runs');
    setTimelineSteps([{ node: 'scout', action: 'queued_job', tokens: 40 }]);
    const runRes = await apiClient.runAgentOnJob(jobId);
    
    // Connect SSE stream
    const evSource = new EventSource(`http://localhost:8000/runs/${runRes.thread_id}/stream`);
    evSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'node_update') {
        setTimelineSteps((prev) => [...prev, data]);
      } else if (data.event === 'completed') {
        evSource.close();
        if (data.interrupted_for_approval && data.proposal_id) {
          setIsInterrupted(true);
          apiClient.getProposalStudio(data.proposal_id).then(setActiveProposal);
        }
      }
    };
  };

  const handleApprovalAction = async (action: 'approve' | 'reject' | 'edit', userText?: string, reason?: string) => {
    if (!activeProposal) return;
    await apiClient.submitApprovalAction({
      thread_id: activeProposal.thread_id,
      action,
      user_edited_text: userText,
      rejection_reason: reason
    });
    alert(`Proposal ${action.toUpperCase()} completed.`);
    setActiveScreen('pipeline');
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 p-5 flex flex-col justify-between">
        <div>
          <h1 className="text-xl font-bold text-sky-400 mb-6 flex items-center gap-2">
            <span>GigBid Copilot</span>
          </h1>
          <nav className="flex flex-col gap-2">
            <button onClick={() => setActiveScreen('inbox')} className={`text-left px-3 py-2 rounded text-sm ${activeScreen === 'inbox' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}>Job Inbox</button>
            <button onClick={() => setActiveScreen('studio')} className={`text-left px-3 py-2 rounded text-sm ${activeScreen === 'studio' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}>Proposal Studio</button>
            <button onClick={() => setActiveScreen('runs')} className={`text-left px-3 py-2 rounded text-sm ${activeScreen === 'runs' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}>Agent Run Viewer</button>
            <button onClick={() => setActiveScreen('analytics')} className={`text-left px-3 py-2 rounded text-sm ${activeScreen === 'analytics' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}>Analytics</button>
            <button onClick={() => setActiveScreen('settings')} className={`text-left px-3 py-2 rounded text-sm ${activeScreen === 'settings' ? 'bg-sky-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}>Settings & Memory</button>
          </nav>
        </div>
        <div className="border-t border-slate-800 pt-4 text-xs text-slate-400">
          <p className="font-semibold text-slate-200">Dr. Sarah Chen</p>
          <p>AI/ML Engineer · 120 Connects</p>
        </div>
      </aside>

      {/* Main Container */}
      <main className="flex-1 p-8 overflow-y-auto">
        {activeScreen === 'inbox' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Job Inbox</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {jobs.map((j) => (
                <div key={j.id} className="bg-slate-900 border border-slate-800 p-5 rounded-lg">
                  <div className="flex justify-between items-center text-xs text-slate-400 mb-2">
                    <span>Client Spend: ${j.client_spend}</span>
                    <span className="bg-sky-950 text-sky-400 px-2 py-0.5 rounded">{j.connects_cost} Connects</span>
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{j.title}</h3>
                  <p className="text-slate-300 text-sm mb-4 line-clamp-3">{j.description}</p>
                  <button
                    onClick={() => handleRunCopilot(j.id)}
                    className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-semibold px-4 py-2 rounded text-xs"
                  >
                    Run GigBid Copilot
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeScreen === 'studio' && activeProposal && (
          <div>
            <h2 className="text-2xl font-bold mb-2">Proposal Studio</h2>
            <p className="text-slate-400 text-sm mb-4">Every claim is grounded in portfolio evidence. Hover over sentences to view citations.</p>
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg leading-relaxed">
              {activeProposal.claims_hover_data.map((c, idx) => (
                <EvidenceHover key={idx} claim={c} />
              ))}
            </div>
            <ApprovalPanel
              threadId={activeProposal.thread_id}
              bidAmount={activeProposal.bid_amount}
              connectsCost={activeProposal.connects_cost}
              dryRunPreview={activeProposal.dry_run_preview}
              onAction={handleApprovalAction}
            />
          </div>
        )}

        {activeScreen === 'runs' && (
          <div>
            <h2 className="text-2xl font-bold mb-4">Agent Run Viewer</h2>
            <RunTimeline steps={timelineSteps} isInterrupted={isInterrupted} />
            {isInterrupted && (
              <button
                onClick={() => setActiveScreen('studio')}
                className="mt-4 bg-sky-500 text-slate-950 px-4 py-2 rounded text-sm font-semibold"
              >
                Open Proposal Studio
              </button>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
