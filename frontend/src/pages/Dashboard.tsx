import React from "react";
import { 
  Files, 
  Search, 
  Network, 
  Workflow,
  Sparkles,
  Cpu
} from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { name: "Mon", offline: 4200, cloud: 2400 },
  { name: "Tue", offline: 3000, cloud: 1398 },
  { name: "Wed", offline: 5800, cloud: 8800 },
  { name: "Thu", offline: 2780, cloud: 3908 },
  { name: "Fri", offline: 4900, cloud: 4800 },
  { name: "Sat", offline: 6390, cloud: 3800 },
  { name: "Sun", offline: 7490, cloud: 4300 },
];

export const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* System Status Banner */}
      <div className="bg-card border border-border rounded-xl p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-sm">
        <div className="text-left">
          <h2 className="text-xl font-bold text-foreground">Workspace Dashboard</h2>
          <p className="text-muted-foreground text-sm">Enterprise Intelligence Operating System • Connected Hybrid Model</p>
        </div>
        <div className="flex gap-2.5">
          <span className="flex items-center gap-1.5 px-3 py-1 bg-green-500/10 text-green-600 dark:text-green-400 text-xs font-semibold rounded-full border border-green-500/20">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
            Ollama Offline: Connected
          </span>
          <span className="flex items-center gap-1.5 px-3 py-1 bg-primary/10 text-primary text-xs font-semibold rounded-full border border-primary/20">
            <Sparkles className="w-3.5 h-3.5" />
            Gemini Cloud: Active
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { title: "Indexed Documents", value: "1,248", icon: Files, change: "+12.3% vs last week" },
          { title: "Vector Nodes (Chroma)", value: "482,901", icon: Search, change: "99.8% semantic index" },
          { title: "Entity Relations (Neo4j)", value: "24,810", icon: Network, change: "Graph database active" },
          { title: "Active Workflows", value: "14", icon: Workflow, change: "3,891 executions today" },
        ].map((metric, i) => {
          const Icon = metric.icon;
          return (
            <div key={i} className="bg-card border border-border rounded-xl p-5 space-y-4 hover:border-primary/40 transition-colors shadow-sm text-left">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{metric.title}</span>
                <div className="w-8 h-8 rounded bg-muted flex items-center justify-center text-muted-foreground">
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-foreground">{metric.value}</h3>
                <span className="text-xs text-muted-foreground">{metric.change}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts & Infrastructure Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Token Consumption Recharts */}
        <div className="bg-card border border-border rounded-xl p-5 lg:col-span-2 space-y-4 shadow-sm text-left">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold text-foreground">Token Consumption Analytics</h3>
              <p className="text-xs text-muted-foreground">Comparison of locally processed tokens vs cloud processing API</p>
            </div>
            <div className="flex gap-4 text-xs font-medium">
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-primary rounded" /> Offline (Ollama)</span>
              <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-cyan-500 rounded" /> Cloud (Gemini)</span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ left: -10, right: 10, top: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorOffline" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorCloud" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
                <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", color: "hsl(var(--card-foreground))" }} />
                <Area type="monotone" dataKey="offline" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#colorOffline)" strokeWidth={2} />
                <Area type="monotone" dataKey="cloud" stroke="#06b6d4" fillOpacity={1} fill="url(#colorCloud)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Providers Overview */}
        <div className="bg-card border border-border rounded-xl p-5 space-y-4 shadow-sm text-left">
          <div>
            <h3 className="text-sm font-semibold text-foreground">AI Provider Configuration</h3>
            <p className="text-xs text-muted-foreground">Dynamic cognitive model routing layer status</p>
          </div>
          <div className="space-y-3">
            {[
              { provider: "Ollama (Offline)", model: "llama3.2:3b", type: "Active", isDefault: true, icon: Cpu },
              { provider: "Google Gemini", model: "gemini-2.5-flash", type: "Active", isDefault: false, icon: Sparkles },
              { provider: "Anthropic", model: "claude-3-5-sonnet", type: "Available", isDefault: false, icon: Sparkles },
              { provider: "DeepSeek", model: "deepseek-coder", type: "Available", isDefault: false, icon: Cpu },
            ].map((prov, i) => {
              const Icon = prov.icon;
              return (
                <div key={i} className="flex items-center justify-between p-3 bg-muted/40 rounded-lg border border-border/60">
                  <div className="flex flex-col text-left">
                    <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                      {prov.provider}
                      {prov.isDefault && <span className="text-[9px] bg-primary text-primary-foreground px-1.5 py-0.5 rounded font-normal">default</span>}
                    </span>
                    <span className="text-[10px] text-muted-foreground font-mono mt-0.5 flex items-center gap-1">
                      <Icon className="w-3 h-3" /> {prov.model}
                    </span>
                  </div>
                  <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full border ${prov.type === "Active" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-muted text-muted-foreground border-border"}`}>
                    {prov.type}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
