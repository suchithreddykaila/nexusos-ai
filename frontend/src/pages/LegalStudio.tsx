import React, { useState, useEffect } from "react";
import { 
  Briefcase, Plus, Scale, ShieldAlert, CheckCircle, FileText, Cpu, ChevronRight, Clock, Scale3d, Search
} from "lucide-react";
import { useAuthStore } from "../store/auth";
import { useWorkspaceStore } from "../store/workspace";
import { useKnowledgeStore } from "../store/knowledge";
import { useLegalStore } from "../store/legal";
import type { LegalMatter, ContractAnalysis, ExtractedClause, TimelineEvent, RiskProfile } from "../store/legal";
import { cn } from "../utils/cn";

export const LegalStudio: React.FC = () => {
  const { accessToken } = useAuthStore();
  const { activeWorkspace } = useWorkspaceStore();
  const { assets } = useKnowledgeStore();
  
  const { 
    matters, 
    activeMatter, 
    activeAnalysis, 
    isLoading, 
    setMatters, 
    setActiveMatter, 
    setActiveAnalysis,
    setLoading
  } = useLegalStore();

  const [activeRightTab, setActiveRightTab] = useState<"risk" | "timeline" | "compliance" | "clauses">("clauses");
  const [chatInput, setChatInput] = useState("");
  const [chatLog, setChatLog] = useState<Array<{ role: string; content: string }>>([]);

  // Mock initial fetch
  useEffect(() => {
    if (accessToken && activeWorkspace?.id) {
      setLoading(true);
      // In a real app we'd call the API here. Mocking for UI development.
      setTimeout(() => {
        setMatters([
          {
            id: "m1", workspace_id: activeWorkspace.id, name: "Acquisition of TechCorp", client_name: "MegaGlobal", status: "Active", is_pinned: true, created_at: new Date().toISOString(), updated_at: new Date().toISOString()
          },
          {
            id: "m2", workspace_id: activeWorkspace.id, name: "Q3 Vendor Agreements", client_name: "Internal", status: "Active", is_pinned: false, created_at: new Date().toISOString(), updated_at: new Date().toISOString()
          }
        ]);
        setLoading(false);
      }, 500);
    }
  }, [accessToken, activeWorkspace, setMatters, setLoading]);

  const handleAnalyzeMock = () => {
    setActiveAnalysis({
      id: "a1",
      matter_id: activeMatter?.id || "m1",
      asset_id: "doc1",
      workspace_id: activeWorkspace?.id || "w1",
      executive_summary: "This is a mutual non-disclosure agreement protecting the exchange of technical and business information.",
      clauses: [
        { id: "c1", category: "Definitions", text: "'Confidential Information' means all non-public information.", confidence_score: 0.99, is_ambiguous: false, is_one_sided: false },
        { id: "c2", category: "Liability", text: "Liability is capped at $1,000,000.", confidence_score: 0.95, is_ambiguous: false, is_one_sided: false, explanation_plain_english: "If someone sues, the max they can get is 1 million dollars." },
        { id: "c3", category: "Termination", text: "Either party may terminate upon 30 days written notice.", confidence_score: 0.98, is_ambiguous: false, is_one_sided: false }
      ],
      risk_profile: {
        risk_score: 25,
        level: "Low",
        high_risk_clauses: [],
        missing_clauses: ["Governing Law"],
        compliance_concerns: [],
        summary: "Standard mutual NDA with mutual termination rights and balanced liability caps."
      },
      timeline: [
        { date: "Effective Date", event_type: "Start", description: "The agreement begins on the date of final signature." },
        { date: "Term + 3 Years", event_type: "Expiration", description: "Confidentiality obligations survive for 3 years after termination." }
      ],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
  };

  const handleChat = () => {
    if (!chatInput.trim()) return;
    setChatLog(prev => [...prev, { role: "user", content: chatInput }]);
    const query = chatInput;
    setChatInput("");
    setLoading(true);
    
    // Mock response
    setTimeout(() => {
      setChatLog(prev => [...prev, { role: "assistant", content: `I have analyzed your request regarding: "${query}". Based on the loaded contract, there are standard indemnification clauses in Section 4.` }]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="flex h-full w-full bg-background overflow-hidden">
      
      {/* LEFT: Matter Sidebar */}
      <div className="w-64 border-r border-border bg-card/30 flex flex-col">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Scale className="w-5 h-5 text-primary" />
            <h2 className="font-semibold">Legal Matters</h2>
          </div>
          <button className="p-1 hover:bg-white/5 rounded-md transition-colors">
            <Plus className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>
        <div className="p-2 flex-1 overflow-y-auto">
          {matters.map(m => (
            <button 
              key={m.id}
              onClick={() => setActiveMatter(m)}
              className={cn(
                "w-full text-left p-2 text-sm rounded-md transition-colors mb-1 flex items-start space-x-2",
                activeMatter?.id === m.id ? "bg-primary/20 text-primary-foreground" : "hover:bg-white/5 text-muted-foreground"
              )}
            >
              <Briefcase className="w-4 h-4 mt-0.5 opacity-70" />
              <div className="flex flex-col">
                <span className="font-medium truncate">{m.name}</span>
                <span className="text-xs opacity-60 truncate">{m.client_name || "Internal"}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* CENTER: Main Viewer & AI Chat */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="h-14 border-b border-border bg-card/50 flex items-center px-4 justify-between backdrop-blur-md">
          <h1 className="text-lg font-semibold flex items-center">
            {activeMatter ? activeMatter.name : "Select a Matter"}
            {activeMatter && <ChevronRight className="w-4 h-4 mx-2 text-muted-foreground" />}
            {activeAnalysis && <span className="text-primary text-sm font-normal bg-primary/10 px-2 py-0.5 rounded">Contract Analysis Active</span>}
          </h1>
          <button 
            onClick={handleAnalyzeMock}
            disabled={!activeMatter}
            className="flex items-center space-x-2 bg-primary/20 hover:bg-primary/30 text-primary-foreground px-3 py-1.5 rounded-md text-sm transition-colors disabled:opacity-50"
          >
            <Cpu className="w-4 h-4" />
            <span>Analyze Contract</span>
          </button>
        </div>

        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {!activeAnalysis ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
              <Scale3d className="w-16 h-16 mb-4 opacity-20" />
              <p>Select a legal matter and analyze a contract to begin.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Executive Summary */}
              <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <h3 className="text-sm font-semibold text-muted-foreground mb-2 uppercase tracking-wider">Executive Summary</h3>
                <p className="text-foreground leading-relaxed">{activeAnalysis.executive_summary}</p>
              </div>

              {/* Chat Log */}
              {chatLog.length > 0 && (
                <div className="space-y-4">
                  {chatLog.map((msg, idx) => (
                    <div key={idx} className={cn("p-4 rounded-xl max-w-[85%]", msg.role === "user" ? "bg-primary/20 ml-auto" : "bg-card border border-border mr-auto")}>
                      <div className="flex items-center space-x-2 mb-1">
                        {msg.role === "user" ? <div className="w-2 h-2 rounded-full bg-primary" /> : <Cpu className="w-4 h-4 text-primary" />}
                        <span className="text-xs font-semibold uppercase tracking-wider opacity-70">{msg.role === "user" ? "You" : "Nyra Legal AI"}</span>
                      </div>
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t border-border bg-background">
          <div className="relative max-w-4xl mx-auto">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleChat()}
              disabled={!activeAnalysis || isLoading}
              placeholder="Ask Nyra to explain a clause, compare documents, or check compliance..."
              className="w-full bg-card border border-border rounded-xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 transition-shadow disabled:opacity-50"
            />
            <button 
              onClick={handleChat}
              disabled={!chatInput.trim() || isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isLoading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Search className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* RIGHT: Intelligence Panel */}
      <div className="w-80 border-l border-border bg-card/30 flex flex-col">
        <div className="flex border-b border-border bg-card/50">
          {[
            { id: "clauses", icon: FileText, label: "Clauses" },
            { id: "risk", icon: ShieldAlert, label: "Risk" },
            { id: "timeline", icon: Clock, label: "Dates" },
            { id: "compliance", icon: CheckCircle, label: "Verify" }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveRightTab(tab.id as any)}
              className={cn(
                "flex-1 py-3 text-xs font-medium flex flex-col items-center justify-center space-y-1 transition-colors border-b-2",
                activeRightTab === tab.id ? "border-primary text-primary bg-primary/5" : "border-transparent text-muted-foreground hover:bg-white/5 hover:text-foreground"
              )}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {!activeAnalysis ? (
            <div className="text-center text-sm text-muted-foreground mt-10">
              Analysis required to view insights.
            </div>
          ) : (
            <>
              {activeRightTab === "clauses" && (
                <div className="space-y-3">
                  {activeAnalysis.clauses.map(clause => (
                    <div key={clause.id} className="bg-background border border-border rounded-lg p-3 text-sm shadow-sm hover:border-primary/50 cursor-pointer transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-primary">{clause.category}</span>
                        {clause.confidence_score > 0.9 && <span className="text-[10px] bg-green-500/20 text-green-400 px-1.5 py-0.5 rounded">High Match</span>}
                      </div>
                      <p className="text-muted-foreground line-clamp-3 mb-2">{clause.text}</p>
                      {clause.explanation_plain_english && (
                        <div className="mt-2 pt-2 border-t border-border/50 text-xs">
                          <span className="font-semibold opacity-70">Explanation:</span> {clause.explanation_plain_english}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {activeRightTab === "risk" && activeAnalysis.risk_profile && (
                <div className="space-y-4">
                  <div className="bg-background border border-border rounded-lg p-4 text-center shadow-sm">
                    <div className="text-4xl font-bold text-green-500 mb-1">{activeAnalysis.risk_profile.risk_score}</div>
                    <div className="text-sm font-medium uppercase tracking-wider text-muted-foreground">Overall Risk ({activeAnalysis.risk_profile.level})</div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Missing Clauses</h4>
                    {activeAnalysis.risk_profile.missing_clauses.map(mc => (
                      <div key={mc} className="flex items-center space-x-2 text-sm bg-red-500/10 text-red-400 border border-red-500/20 rounded p-2">
                        <ShieldAlert className="w-4 h-4" />
                        <span>{mc}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeRightTab === "timeline" && (
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
                  {activeAnalysis.timeline.map((event, i) => (
                    <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                      <div className="flex items-center justify-center w-4 h-4 rounded-full border border-primary bg-background shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10" />
                      <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] p-3 rounded-lg border border-border bg-background shadow-sm">
                        <div className="text-xs font-bold text-primary mb-1">{event.date}</div>
                        <div className="text-sm font-semibold">{event.event_type}</div>
                        <div className="text-xs text-muted-foreground mt-1">{event.description}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeRightTab === "compliance" && (
                <div className="text-center text-sm text-muted-foreground mt-10">
                  Run a compliance framework audit to view results.
                </div>
              )}
            </>
          )}
        </div>
      </div>

    </div>
  );
};
