import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Clock, ShieldAlert, Cpu } from "lucide-react";

const performanceData = [
  { name: "09:00", database: 12, ai: 180, storage: 15 },
  { name: "10:00", database: 15, ai: 240, storage: 12 },
  { name: "11:00", database: 8, ai: 150, storage: 8 },
  { name: "12:00", database: 32, ai: 490, storage: 28 },
  { name: "13:00", database: 10, ai: 120, storage: 9 },
  { name: "14:00", database: 14, ai: 190, storage: 11 },
];

export const Analytics: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto text-left">
      <div>
        <h2 className="text-xl font-bold text-foreground">Platform Analytics</h2>
        <p className="text-muted-foreground text-sm">Monitor backend API latency, AI execution durations, and cluster resource metrics.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { title: "Average Latency", value: "112ms", desc: "Database & routing responses", icon: Clock },
          { title: "AI Model Execution", value: "1.4s", desc: "Ollama / Gemini response speed", icon: Cpu },
          { title: "System Security Health", value: "Secured", desc: "0 anomalies detected", icon: ShieldAlert },
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <div key={idx} className="bg-card border border-border rounded-xl p-5 flex items-center gap-4 shadow-sm">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center text-primary">
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">{item.title}</span>
                <h4 className="text-lg font-bold text-foreground">{item.value}</h4>
                <p className="text-[11px] text-muted-foreground">{item.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Latency Charts */}
      <div className="bg-card border border-border rounded-xl p-5 space-y-4 shadow-sm">
        <div>
          <h3 className="text-sm font-semibold text-foreground">API Latency Over Time (ms)</h3>
          <p className="text-xs text-muted-foreground">Breakdown of backend database queries, AI processing, and storage operations</p>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
              <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
              <YAxis stroke="hsl(var(--muted-foreground))" fontSize={11} tickLine={false} />
              <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: "8px", color: "hsl(var(--card-foreground))" }} />
              <Line type="monotone" dataKey="ai" name="AI Inference" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="database" name="Database" stroke="#06b6d4" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="storage" name="Storage" stroke="#8b5cf6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
