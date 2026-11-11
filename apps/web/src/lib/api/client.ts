/**
 * Generated TypeScript client from FastAPI OpenAPI schema.
 * Do not hand-edit manually.
 */

export interface JobPosting {
  id: string;
  title: string;
  description: string;
  skills: string[];
  budget: number;
  connects_cost: number;
  client_spend: number;
  client_hire_rate: number;
  client_rating: number;
  status: string;
}

export interface ClaimHoverData {
  claim_text: string;
  status: 'supported' | 'partly_supported' | 'unsupported';
  grounding_score: number;
  evidence_source: string;
}

export interface ProposalDetail {
  proposal_id: string;
  job_id: string;
  thread_id: string;
  cover_letter: string;
  bid_amount: number;
  connects_cost: number;
  evidence_citations: string[];
  claims_hover_data: ClaimHoverData[];
  dry_run_preview: any;
  status: string;
}

export interface ApprovalAction {
  thread_id: string;
  action: 'approve' | 'reject' | 'edit';
  user_edited_text?: string;
  rejection_reason?: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  async getJobs(query: string = '', limit: number = 15): Promise<JobPosting[]> {
    const res = await fetch(`${API_BASE}/jobs?query=${encodeURIComponent(query)}&limit=${limit}`);
    return res.json();
  },

  async runAgentOnJob(jobId: string) {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/run-agent`, { method: 'POST' });
    return res.json();
  },

  async getProposalStudio(proposalId: string): Promise<ProposalDetail> {
    const res = await fetch(`${API_BASE}/proposals/${proposalId}`);
    return res.json();
  },

  async submitApprovalAction(action: ApprovalAction) {
    const res = await fetch(`${API_BASE}/approvals/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(action),
    });
    return res.json();
  },

  async getSettings() {
    const res = await fetch(`${API_BASE}/settings`);
    return res.json();
  },

  async deleteMemoryItem(type: 'style' | 'outcome', id: string) {
    const res = await fetch(`${API_BASE}/settings/memory/${type}/${id}`, { method: 'DELETE' });
    return res.json();
  }
};
