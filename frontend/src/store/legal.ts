import { create } from 'zustand';

export type ClauseCategory = "Definitions" | "Parties" | "Effective Date" | "Expiration" | "Renewal" | "Payment" | "Confidentiality" | "Termination" | "Liability" | "Indemnification" | "Force Majeure" | "Jurisdiction" | "Governing Law" | "Dispute Resolution" | "Data Privacy" | "GDPR" | "Intellectual Property" | "Assignment" | "Warranty" | "Obligations" | "Deadlines" | "Penalties" | "Other";

export type RiskLevel = "Critical" | "High" | "Medium" | "Low" | "Info";

export interface ExtractedClause {
  id: string;
  category: ClauseCategory;
  text: string;
  page_number?: number;
  confidence_score: number;
  explanation_plain_english?: string;
  negotiation_suggestions?: string;
  is_ambiguous: boolean;
  is_one_sided: boolean;
}

export interface RiskProfile {
  risk_score: number;
  level: RiskLevel;
  high_risk_clauses: string[];
  missing_clauses: string[];
  compliance_concerns: string[];
  summary: string;
}

export interface TimelineEvent {
  date: string;
  event_type: string;
  description: string;
  related_clause_id?: string;
}

export interface ContractAnalysis {
  id: string;
  matter_id: string;
  asset_id: string;
  workspace_id: string;
  executive_summary: string;
  clauses: ExtractedClause[];
  risk_profile?: RiskProfile;
  timeline: TimelineEvent[];
  created_at: string;
  updated_at: string;
}

export interface LegalMatter {
  id: string;
  workspace_id: string;
  name: string;
  client_name?: string;
  description?: string;
  status: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

interface LegalState {
  matters: LegalMatter[];
  activeMatter: LegalMatter | null;
  activeAnalysis: ContractAnalysis | null;
  isLoading: boolean;
  error: string | null;
  setMatters: (matters: LegalMatter[]) => void;
  setActiveMatter: (matter: LegalMatter | null) => void;
  setActiveAnalysis: (analysis: ContractAnalysis | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useLegalStore = create<LegalState>((set) => ({
  matters: [],
  activeMatter: null,
  activeAnalysis: null,
  isLoading: false,
  error: null,
  setMatters: (matters) => set({ matters }),
  setActiveMatter: (matter) => set({ activeMatter: matter }),
  setActiveAnalysis: (analysis) => set({ activeAnalysis: analysis }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
}));
