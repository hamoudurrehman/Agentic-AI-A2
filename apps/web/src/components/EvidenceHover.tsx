import React from 'react';
import { ClaimHoverData } from '../lib/api/client';

interface EvidenceHoverProps {
  claim: ClaimHoverData;
}

export const EvidenceHover: React.FC<EvidenceHoverProps> = ({ claim }) => {
  return (
    <span
      className="underline decoration-sky-400 decoration-dashed cursor-help relative group"
      title={`Evidence: ${claim.evidence_source} (Score: ${claim.grounding_score})`}
    >
      {claim.claim_text}{' '}
      <span className="hidden group-hover:block absolute bottom-full left-0 bg-slate-900 text-sky-300 text-xs p-2 rounded shadow-xl border border-slate-700 w-64 z-50">
        <p className="font-bold">Status: {claim.status.toUpperCase()}</p>
        <p>Grounding: {claim.grounding_score * 100}%</p>
        <p className="text-slate-400 mt-1">{claim.evidence_source}</p>
      </span>
    </span>
  );
};
