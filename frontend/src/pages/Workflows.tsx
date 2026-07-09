import React from "react";
import { PlayCircle, Settings, Clock, Plus } from "lucide-react";

export const Workflows: React.FC = () => {
  const workflows = [
    { name: "Legal Document Entity Alignment", desc: "Monitors MinIO bucket for incoming legal agreements, runs entity extraction with Ollama, and maps connections in Neo4j.", status: "Active", execution: "12m ago" },
    { name: "Executive PDF Digest Compiler", desc: "Compiles uploaded PPTX and PDF documents, extracts outlines, translates keywords, and pushes vector indices to ChromaDB.", status: "Active", execution: "1h ago" },
    { name: "Cross-Reference Alert System", desc: "Automated analysis of contract clauses, flags discrepancies, and sends warning diagnostics via webhooks.", status: "Draft", execution: "Never" }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto text-left">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-foreground">Automation Workflows</h2>
          <p className="text-muted-foreground text-sm">Design, trigger, and monitor automated knowledge extraction pipelines.</p>
        </div>
        <button className="flex items-center gap-1.5 px-4 py-2 bg-primary text-primary-foreground font-semibold rounded-lg hover:bg-primary/95 transition-colors text-sm shadow-sm">
          <Plus className="w-4 h-4" /> Create Workflow
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {workflows.map((wf, idx) => (
          <div key={idx} className="bg-card border border-border rounded-xl p-5 flex flex-col justify-between hover:border-primary/40 transition-colors shadow-sm">
            <div className="space-y-3">
              <div className="flex justify-between items-start">
                <h3 className="font-semibold text-foreground text-sm">{wf.name}</h3>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  wf.status === "Active" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-muted text-muted-foreground border-border"
                }`}>
                  {wf.status}
                </span>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">{wf.desc}</p>
            </div>
            <div className="flex items-center justify-between border-t border-border mt-5 pt-4 text-xs">
              <span className="text-muted-foreground flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> Run: {wf.execution}
              </span>
              <div className="flex gap-1.5">
                <button className="p-1 hover:bg-muted text-muted-foreground hover:text-foreground rounded transition-colors" title="Settings">
                  <Settings className="w-4 h-4" />
                </button>
                <button className="p-1 hover:bg-muted text-primary hover:text-primary/80 rounded transition-colors" title="Run now">
                  <PlayCircle className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
