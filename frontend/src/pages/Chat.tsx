import React, { useState, useEffect, useRef } from "react";
import { Send, Trash2, Cpu, FileText, ChevronRight, MessageSquare, Layers, Folder } from "lucide-react";
import { useChatStore } from "../store/chat";
import { useKnowledgeStore } from "../store/knowledge";
import { useWorkspaceStore } from "../store/workspace";
import { useAuthStore } from "../store/auth";
import { cn } from "../utils/cn";

export const Chat: React.FC = () => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { 
    messages, 
    citations, 
    loading, 
    preferredProvider, 
    activeProjectId, 
    activeCollectionId,
    setPreferredProvider, 
    setProjectFilter, 
    setCollectionFilter, 
    clearChat, 
    sendMessage 
  } = useChatStore();

  const { accessToken } = useAuthStore();
  const { projects, collections, fetchProjects, fetchCollections } = useKnowledgeStore();
  const { activeWorkspace } = useWorkspaceStore();

  useEffect(() => {
    if (accessToken && activeWorkspace?.id) {
      fetchProjects(accessToken, activeWorkspace.id);
    }
  }, [accessToken, activeWorkspace, fetchProjects]);

  useEffect(() => {
    if (accessToken && activeProjectId) {
      fetchCollections(accessToken, activeProjectId);
    }
  }, [accessToken, activeProjectId, fetchCollections]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading || !activeWorkspace) return;
    sendMessage(input, activeWorkspace.id, accessToken);
    setInput("");
  };

  const suggestedPrompts = [
    "Summarize recent project specs",
    "Compare draft contracts and policy manuals",
    "Explain retention policy regulations",
  ];

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background overflow-hidden relative">
      {/* Main chat window */}
      <div className="flex-1 flex flex-col h-full border-r border-border">
        {/* Chat Control Toolbar Header */}
        <div className="h-14 border-b border-border flex items-center justify-between px-6 shrink-0 bg-card/50 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <Cpu className="w-5 h-5 text-primary animate-pulse" />
            <span className="text-sm font-semibold">AI Intelligence Core</span>
          </div>

          <div className="flex items-center gap-3">
            {/* Project Filter */}
            <div className="flex items-center gap-1.5">
              <Folder className="w-4 h-4 text-muted-foreground" />
              <select
                value={activeProjectId || ""}
                onChange={(e) => setProjectFilter(e.target.value || null)}
                className="text-xs bg-muted border border-border rounded px-2 py-1 focus:outline-none text-foreground"
              >
                <option value="">All Projects</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {/* Collection Filter */}
            {activeProjectId && (
              <div className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-muted-foreground" />
                <select
                  value={activeCollectionId || ""}
                  onChange={(e) => setCollectionFilter(e.target.value || null)}
                  className="text-xs bg-muted border border-border rounded px-2 py-1 focus:outline-none text-foreground"
                >
                  <option value="">All Collections</option>
                  {collections.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Provider Switcher */}
            <select
              value={preferredProvider}
              onChange={(e) => setPreferredProvider(e.target.value)}
              className="text-xs bg-muted border border-border rounded px-2 py-1 focus:outline-none font-medium text-foreground"
            >
              <option value="ollama">Ollama (Offline)</option>
              <option value="gemini">Gemini (Cloud)</option>
            </select>

            <button
              onClick={clearChat}
              className="p-1.5 hover:bg-muted text-muted-foreground hover:text-destructive rounded transition-colors"
              title="Clear active session logs"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Messaging Box stream */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-md mx-auto text-center space-y-6">
              <MessageSquare className="w-12 h-12 text-muted-foreground/30" />
              <div>
                <h3 className="text-lg font-semibold mb-1 text-foreground">Knowledge Engine Workspace</h3>
                <p className="text-sm text-muted-foreground">
                  Ask context-aware questions, compare project files, or generate cited summaries.
                </p>
              </div>

              {/* Suggest Prompt Cards Grid */}
              <div className="grid gap-2.5 w-full">
                {suggestedPrompts.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => setInput(prompt)}
                    className="p-3 bg-muted/50 hover:bg-muted border border-border hover:border-primary/30 rounded-lg text-left text-xs font-medium text-foreground transition-all flex items-center justify-between"
                  >
                    <span>{prompt}</span>
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={cn(
                  "p-4 rounded-xl max-w-3xl border text-sm relative transition-all animate-in fade-in slide-in-from-bottom-2",
                  msg.role === "user"
                    ? "bg-primary/5 border-primary/20 text-foreground ml-auto"
                    : "bg-card border-border text-foreground mr-auto"
                )}
              >
                <div className="font-semibold text-xs text-muted-foreground mb-1.5 uppercase tracking-wider">
                  {msg.role === "user" ? "You" : "NexusOS AI"}
                </div>
                <div className="leading-relaxed whitespace-pre-wrap">{msg.content}</div>

                {/* Inline Citations indicator list */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-border flex flex-wrap gap-2">
                    {msg.citations.map((c) => (
                      <span 
                        key={c.id}
                        className="px-2 py-0.5 bg-muted border border-border hover:border-primary text-[10px] rounded font-semibold cursor-pointer text-foreground transition-colors"
                        title={c.snippet}
                      >
                        [{c.id}] {c.asset_name}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-1.5 items-center text-xs text-muted-foreground italic pl-2">
              <Cpu className="w-3.5 h-3.5 animate-spin" />
              Thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Query Prompt Field form */}
        <form onSubmit={handleSubmit} className="p-4 border-t border-border shrink-0 bg-card/30">
          <div className="relative max-w-3xl mx-auto">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything about workspace knowledge..."
              disabled={loading}
              className="w-full bg-card border border-border focus:border-primary rounded-xl pl-4 pr-12 py-3.5 text-sm focus:outline-none transition-all text-foreground shadow-sm"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2.5 top-2.5 p-2 bg-primary text-primary-foreground disabled:bg-muted disabled:text-muted-foreground rounded-lg transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>

      {/* Right Citations Panel */}
      {citations.length > 0 && (
        <aside className="w-80 h-full bg-card/30 p-5 overflow-y-auto hidden lg:block animate-in slide-in-from-right-3 border-l border-border">
          <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-4">
            Source Citations ({citations.length})
          </h3>
          <div className="space-y-3">
            {citations.map((cit) => (
              <div 
                key={cit.id}
                className="p-3 bg-card border border-border hover:border-primary rounded-lg transition-all group"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <FileText className="w-4 h-4 text-primary" />
                  <span className="text-xs font-semibold truncate block max-w-[150px] text-foreground">
                    {cit.asset_name}
                  </span>
                  <span className="ml-auto text-[10px] font-mono bg-muted px-1.5 py-0.5 rounded text-muted-foreground">
                    {Math.round(cit.confidence_score * 100)}% Match
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground leading-relaxed italic line-clamp-3 group-hover:line-clamp-none transition-all duration-300">
                  &ldquo;{cit.snippet}&rdquo;
                </p>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  );
};
