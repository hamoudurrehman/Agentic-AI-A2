import React, { useState } from 'react';

interface ApprovalPanelProps {
  threadId: string;
  bidAmount: number;
  connectsCost: number;
  dryRunPreview: any;
  onAction: (action: 'approve' | 'reject' | 'edit', editedText?: string, reason?: string) => void;
}

export const ApprovalPanel: React.FC<ApprovalPanelProps> = ({
  threadId,
  bidAmount,
  connectsCost,
  dryRunPreview,
  onAction,
}) => {
  const [rejectionReason, setRejectionReason] = useState('');

  return (
    <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 mt-4">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-semibold text-sky-400">Human Approval Gate (LangGraph Interrupt)</h4>
        <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-1 rounded-full">Requires Confirmation</span>
      </div>
      <div className="text-sm text-slate-300 mb-4">
        <p>Bid Amount: <strong>${bidAmount}</strong> | Connects Required: <strong>{connectsCost}</strong></p>
        <p className="text-xs text-slate-400 mt-1">Idempotency Key: sub_{threadId} | Pre-submission verification complete.</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onAction('approve')}
          className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded"
        >
          Approve & Dispatch
        </button>
        <button
          onClick={() => onAction('edit')}
          className="bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-semibold px-4 py-2 rounded"
        >
          Save Edits & Submit
        </button>
        <button
          onClick={() => onAction('reject', undefined, rejectionReason || 'User manual rejection')}
          className="bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold px-4 py-2 rounded"
        >
          Reject Bid
        </button>
      </div>
    </div>
  );
};
