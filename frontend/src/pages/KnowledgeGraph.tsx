import React from "react";
import { RefreshCw, ZoomIn, ZoomOut } from "lucide-react";

export const KnowledgeGraph: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto text-left h-full flex flex-col">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-foreground">Knowledge Graph Explorer</h2>
          <p className="text-muted-foreground text-sm">Visualize entity extractions, node relationships, and transactional database maps generated from documents.</p>
        </div>
        <div>
          <button className="flex items-center gap-1.5 px-3 py-1.5 bg-muted hover:bg-muted/80 text-foreground border border-border text-xs rounded-lg transition-colors font-medium">
            <RefreshCw className="w-3.5 h-3.5" /> Rebuild Graph
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1 min-h-[500px]">
        {/* Graph Properties Sidebar */}
        <div className="bg-card border border-border rounded-xl p-5 space-y-5 text-sm self-start shadow-sm">
          <div className="space-y-1">
            <h3 className="font-semibold text-foreground">Graph Properties</h3>
            <p className="text-xs text-muted-foreground">Toggle layers and configure schema nodes</p>
          </div>

          <div className="space-y-2 border-t border-border pt-4">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Node Classifications</span>
            <div className="space-y-2 mt-2">
              <span className="flex items-center gap-2 text-xs font-medium"><span className="w-3 h-3 rounded-full bg-indigo-500" /> Documents</span>
              <span className="flex items-center gap-2 text-xs font-medium"><span className="w-3 h-3 rounded-full bg-cyan-500" /> Organizations</span>
              <span className="flex items-center gap-2 text-xs font-medium"><span className="w-3 h-3 rounded-full bg-amber-500" /> Persons</span>
              <span className="flex items-center gap-2 text-xs font-medium"><span className="w-3 h-3 rounded-full bg-red-500" /> Locations</span>
              <span className="flex items-center gap-2 text-xs font-medium"><span className="w-3 h-3 rounded-full bg-green-500" /> Concepts/Topics</span>
            </div>
          </div>

          <div className="space-y-2 border-t border-border pt-4">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Neo4j Endpoint</span>
            <div className="p-3 bg-muted/50 border border-border rounded-lg text-xs font-mono break-all mt-1">
              bolt://localhost:7687
              <div className="text-[10px] text-green-500 font-semibold mt-1">Connected: Community Edition</div>
            </div>
          </div>
        </div>

        {/* Visualizer Canvas Area */}
        <div className="bg-card border border-border rounded-xl lg:col-span-3 flex flex-col justify-between overflow-hidden relative min-h-[450px] shadow-sm">
          {/* HUD Toolbar */}
          <div className="absolute top-4 left-4 z-10 flex gap-1 bg-card/85 border border-border px-2 py-1.5 rounded-lg shadow-md backdrop-blur-sm">
            <button className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground" title="Zoom in"><ZoomIn className="w-4 h-4" /></button>
            <button className="p-1 hover:bg-muted rounded text-muted-foreground hover:text-foreground" title="Zoom out"><ZoomOut className="w-4 h-4" /></button>
            <span className="w-[1px] bg-border mx-1" />
            <span className="text-xs font-semibold text-muted-foreground px-2 py-1 select-none">Nodes: 124 • Relations: 591</span>
          </div>

          {/* Interactive Simulated Graph Canvas */}
          <div className="flex-1 flex items-center justify-center bg-muted/20 relative overflow-hidden">
            <svg className="w-full h-full min-h-[400px] opacity-75 dark:opacity-90" viewBox="0 0 800 500">
              {/* Connection Lines (Relations) */}
              <line x1="400" y1="250" x2="250" y2="150" stroke="hsl(var(--border))" strokeWidth="1.5" />
              <line x1="400" y1="250" x2="550" y2="150" stroke="hsl(var(--border))" strokeWidth="1.5" strokeDasharray="4" />
              <line x1="400" y1="250" x2="350" y2="380" stroke="hsl(var(--border))" strokeWidth="1.5" />
              <line x1="400" y1="250" x2="480" y2="380" stroke="hsl(var(--border))" strokeWidth="1.5" />
              <line x1="250" y1="150" x2="150" y2="220" stroke="hsl(var(--border))" strokeWidth="1" />
              <line x1="250" y1="150" x2="200" y2="80" stroke="hsl(var(--border))" strokeWidth="1" />
              <line x1="550" y1="150" x2="680" y2="180" stroke="hsl(var(--border))" strokeWidth="1" />

              {/* Circles (Nodes) */}
              {/* Document Center Node */}
              <circle cx="400" cy="250" r="16" className="fill-primary stroke-background" strokeWidth="2.5" />
              <text x="400" y="285" textAnchor="middle" className="fill-foreground font-sans text-xs font-semibold">annual_financial_report.pdf</text>

              {/* Organizations Node */}
              <circle cx="250" cy="150" r="12" className="fill-cyan-500 stroke-background" strokeWidth="2" />
              <text x="250" y="128" textAnchor="middle" className="fill-foreground font-sans text-[10px] font-medium">Acme Corp</text>

              {/* Persons Node */}
              <circle cx="550" cy="150" r="12" className="fill-amber-500 stroke-background" strokeWidth="2" />
              <text x="550" y="128" textAnchor="middle" className="fill-foreground font-sans text-[10px] font-medium">Suchith K. (Author)</text>

              {/* Locations Node */}
              <circle cx="350" cy="380" r="12" className="fill-red-500 stroke-background" strokeWidth="2" />
              <text x="350" y="410" textAnchor="middle" className="fill-foreground font-sans text-[10px] font-medium">Hyderabad</text>

              {/* Concepts Node */}
              <circle cx="480" cy="380" r="12" className="fill-green-500 stroke-background" strokeWidth="2" />
              <text x="480" y="410" textAnchor="middle" className="fill-foreground font-sans text-[10px] font-medium">Revenue Growth</text>

              {/* Child Nodes */}
              <circle cx="150" cy="220" r="8" className="fill-cyan-400 stroke-background" strokeWidth="1.5" />
              <circle cx="200" cy="80" r="8" className="fill-cyan-400 stroke-background" strokeWidth="1.5" />
              <circle cx="680" cy="180" r="8" className="fill-amber-400 stroke-background" strokeWidth="1.5" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};
