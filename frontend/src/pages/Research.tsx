import React, { useState, useEffect } from "react";
import { 
  FileText, Cpu, Plus, Sparkles, Send, Trash2, Library, BookOpen, 
  Map, FileCheck, CheckSquare, Square, Clipboard, ChevronRight, Download 
} from "lucide-react";
import { useAuthStore } from "../store/auth";
import { useWorkspaceStore } from "../store/workspace";
import { useKnowledgeStore } from "../store/knowledge";
import { useResearchStore } from "../store/research";
import type { ResearchSession, ResearchNote } from "../store/research";
import { cn } from "../utils/cn";

export const Research: React.FC = () => {
  const { accessToken } = useAuthStore();
  const { activeWorkspace } = useWorkspaceStore();
  const { assets, fetchAssets } = useKnowledgeStore();
  
  const { 
    sessions, 
    activeSession, 
    notes, 
    bibliography, 
    insights, 
    fetchSessions, 
    createSession, 
    fetchNotes, 
    createNote, 
    updateNote, 
    deleteNote, 
    generateCitations, 
    fetchInsights,
    setActiveSession 
  } = useResearchStore();

  const [activeTab, setActiveTab] = useState<"sources" | "notes" | "citations" | "insights">("sources");
  const [selectedAssetIds, setSelectedAssetIds] = useState<string[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLog, setChatLog] = useState<Array<{ role: string; content: string }>>([]);
  const [loadingAI, setLoadingAI] = useState(false);
  const [sessionName, setSessionName] = useState("");
  
  // Note Form states
  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [selectedNote, setSelectedNote] = useState<ResearchNote | null>(null);

  useEffect(() => {
    if (accessToken && activeWorkspace?.id) {
      fetchSessions(accessToken, activeWorkspace.id);
      fetchAssets(accessToken, activeWorkspace.id);
    }
  }, [accessToken, activeWorkspace, fetchSessions, fetchAssets]);

  useEffect(() => {
    if (accessToken && activeSession?.id) {
      fetchNotes(accessToken, activeSession.id);
    }
  }, [accessToken, activeSession, fetchNotes]);

  const handleCreateSession = async () => {
    if (!sessionName.trim() || !accessToken || !activeWorkspace) return;
    await createSession(accessToken, activeWorkspace.id, sessionName, "Research Studio Study Workspace", selectedAssetIds);
    setSessionName("");
  };

  const handleToggleAsset = (assetId: string) => {
    setSelectedAssetIds((prev) => 
      prev.includes(assetId) ? prev.filter((id) => id !== assetId) : [...prev, assetId]
    );
  };

  const handleAIQuery = async (queryText: string, type: "query" | "compare" | "lit-review" | "summary") => {
    if (!accessToken || !activeWorkspace) return;
    setLoadingAI(true);
    
    // Add user query
    setChatLog((prev) => [...prev, { role: "user", content: queryText }]);
    
    let route = "query";
    if (type === "compare") route = "compare";
    if (type === "lit-review") route = "literature-review";
    if (type === "summary") route = "summary";

    try {
      const response = await fetch(`http://localhost:8000/api/v1/research/${route}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          query: queryText,
          workspace_id: activeWorkspace.id,
          asset_ids: selectedAssetIds.length > 0 ? selectedAssetIds : (activeSession?.asset_ids || []),
          preferred_provider: "ollama"
        })
      });

      if (response.ok) {
        const data = await response.json();
        setChatLog((prev) => [...prev, { role: "assistant", content: data.response_text }]);
      } else {
        setChatLog((prev) => [...prev, { role: "assistant", content: "Error: AI engine unreachable." }]);
      }
    } catch (e) {
      setChatLog((prev) => [...prev, { role: "assistant", content: "Error communicating with intelligence layers." }]);
    } finally {
      setLoadingAI(false);
    }
  };

  const handleSaveNote = async () => {
    if (!accessToken || !activeSession || !noteTitle.trim()) return;
    if (selectedNote) {
      await updateNote(accessToken, selectedNote.id, noteTitle, noteContent, selectedAssetIds);
    } else {
      await createNote(accessToken, activeSession.id, noteTitle, noteContent, selectedAssetIds);
    }
    setNoteTitle("");
    setNoteContent("");
    setSelectedNote(null);
  };

  const handleGenerateBibliography = async (style: string) => {
    if (!accessToken) return;
    const targetIds = selectedAssetIds.length > 0 ? selectedAssetIds : (activeSession?.asset_ids || []);
    await generateCitations(accessToken, targetIds, style);
  };

  const handleLoadInsights = async () => {
    if (!accessToken) return;
    const targetIds = selectedAssetIds.length > 0 ? selectedAssetIds : (activeSession?.asset_ids || []);
    await fetchInsights(accessToken, targetIds);
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-background text-foreground overflow-hidden">
      {/* Left Workspace Panel: Sessions list and configuration tabs */}
      <aside className="w-80 border-r border-border flex flex-col h-full bg-card/40 shrink-0">
        <div className="p-4 border-b border-border">
          <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2 mb-3">
            <Library className="w-4 h-4 text-primary" />
            Research sessions
          </h2>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Session title..."
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              className="text-xs bg-muted border border-border rounded px-2.5 py-1.5 focus:outline-none flex-1 text-foreground"
            />
            <button
              onClick={handleCreateSession}
              className="p-1.5 bg-primary text-primary-foreground rounded hover:bg-primary/95 transition-all"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Sessions list */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {sessions.map((sess) => (
            <button
              key={sess.id}
              onClick={() => {
                setActiveSession(sess);
                setSelectedAssetIds(sess.asset_ids);
              }}
              className={cn(
                "w-full text-left p-3 rounded-lg border transition-all text-xs font-medium",
                activeSession?.id === sess.id
                  ? "bg-primary/5 border-primary/20 text-foreground"
                  : "border-transparent text-muted-foreground hover:bg-muted"
              )}
            >
              <div className="font-semibold block mb-0.5">{sess.name}</div>
              <div className="text-[10px] text-muted-foreground">{sess.description}</div>
            </button>
          ))}
        </div>
      </aside>

      {/* Main split-screen panel: Chat assistant and active source workspace */}
      <div className="flex-1 flex flex-col border-r border-border h-full">
        {/* Active Session header */}
        <div className="h-14 border-b border-border flex items-center justify-between px-6 shrink-0 bg-card/60 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary" />
            <span className="font-semibold text-sm">
              {activeSession ? activeSession.name : "Select a Research Session to Begin"}
            </span>
          </div>

          <div className="flex gap-2.5">
            <button
              onClick={() => handleAIQuery("Summarize the methodology of selected documents", "summary")}
              disabled={!activeSession || loadingAI}
              className="text-xs bg-muted border border-border hover:border-primary/30 px-3 py-1.5 rounded-lg font-medium transition-all"
            >
              Summarize Sources
            </button>
            <button
              onClick={() => handleAIQuery("Provide a comparative analysis of arguments", "compare")}
              disabled={!activeSession || loadingAI}
              className="text-xs bg-muted border border-border hover:border-primary/30 px-3 py-1.5 rounded-lg font-medium transition-all"
            >
              Compare Papers
            </button>
          </div>
        </div>

        {/* Chat Pane */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {chatLog.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-sm mx-auto space-y-5">
              <Sparkles className="w-10 h-10 text-primary animate-pulse" />
              <div>
                <h4 className="text-sm font-semibold mb-1 text-foreground">AI Research assistant</h4>
                <p className="text-xs text-muted-foreground">
                  Ask questions across all selected sources, find key methodologies, or identify research gaps.
                </p>
              </div>
            </div>
          ) : (
            chatLog.map((log, idx) => (
              <div
                key={idx}
                className={cn(
                  "p-4 rounded-xl text-xs leading-relaxed max-w-2xl border transition-all animate-in fade-in",
                  log.role === "user"
                    ? "bg-primary/5 border-primary/20 text-foreground ml-auto"
                    : "bg-card border-border text-foreground mr-auto"
                )}
              >
                <div className="font-bold text-[10px] uppercase text-muted-foreground tracking-wider mb-1">
                  {log.role === "user" ? "Researcher" : "Assistant Core"}
                </div>
                <div className="whitespace-pre-wrap">{log.content}</div>
              </div>
            ))
          )}
          {loadingAI && (
            <div className="flex gap-1.5 items-center text-xs text-muted-foreground italic pl-2">
              <Cpu className="w-3.5 h-3.5 animate-spin text-primary" />
              Analyzing sources...
            </div>
          )}
        </div>

        {/* Chat prompt field */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (!chatInput.trim() || loadingAI || !activeSession) return;
            handleAIQuery(chatInput, "query");
            setChatInput("");
          }}
          className="p-4 border-t border-border shrink-0 bg-card/30"
        >
          <div className="relative max-w-2xl mx-auto">
            <input
              type="text"
              placeholder="Ask anything about selected papers..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              disabled={loadingAI || !activeSession}
              className="w-full bg-card border border-border focus:border-primary rounded-xl pl-4 pr-12 py-3.5 text-xs focus:outline-none transition-all text-foreground"
            />
            <button
              type="submit"
              disabled={loadingAI || !chatInput.trim() || !activeSession}
              className="absolute right-2.5 top-2.5 p-2 bg-primary text-primary-foreground disabled:bg-muted disabled:text-muted-foreground rounded-lg transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>

      {/* Right panel tabs: Note Editor, Source checkmarks, Bibliography exports */}
      <aside className="w-96 flex flex-col h-full bg-card/25 shrink-0">
        <div className="h-14 border-b border-border flex items-center px-4 gap-1 bg-card/50 shrink-0">
          {(["sources", "notes", "citations", "insights"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                "text-xs px-2.5 py-1.5 rounded font-semibold capitalize transition-all",
                activeTab === tab 
                  ? "bg-primary text-primary-foreground" 
                  : "text-muted-foreground hover:bg-muted"
              )}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {/* Tab 1: Source asset checklists */}
          {activeTab === "sources" && (
            <div className="space-y-3">
              <h3 className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">
                Select Workspace Sources
              </h3>
              <div className="space-y-2">
                {assets.map((asset) => {
                  const isChecked = selectedAssetIds.includes(asset.id);
                  return (
                    <button
                      key={asset.id}
                      onClick={() => handleToggleAsset(asset.id)}
                      className={cn(
                        "w-full text-left p-3 rounded-lg border text-xs flex items-center justify-between transition-all hover:bg-muted",
                        isChecked ? "border-primary/30 bg-primary/5" : "border-border"
                      )}
                    >
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-primary" />
                        <span className="font-semibold block truncate max-w-[200px] text-foreground">
                          {asset.name}
                        </span>
                      </div>
                      {isChecked ? (
                        <FileCheck className="w-4.5 h-4.5 text-primary" />
                      ) : (
                        <div className="w-4.5 h-4.5 border border-border rounded" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 2: Markdown Study Notes */}
          {activeTab === "notes" && (
            <div className="space-y-4">
              <div className="space-y-2 border border-border p-3 rounded-lg bg-card bg-card/60">
                <input
                  type="text"
                  placeholder="Note Title..."
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  className="text-xs bg-muted border border-border rounded px-2.5 py-1.5 focus:outline-none w-full text-foreground"
                />
                <textarea
                  placeholder="Rich Markdown notes content..."
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  rows={4}
                  className="text-xs bg-muted border border-border rounded px-2.5 py-1.5 focus:outline-none w-full text-foreground resize-none"
                />
                <button
                  onClick={handleSaveNote}
                  disabled={!activeSession}
                  className="w-full text-xs py-2 bg-primary text-primary-foreground font-semibold rounded hover:bg-primary/95 transition-all"
                >
                  {selectedNote ? "Update Study Note" : "Save Study Note"}
                </button>
              </div>

              <div className="space-y-2.5">
                <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                  Session Notes Notepad ({notes.length})
                </h4>
                {notes.map((note) => (
                  <div key={note.id} className="p-3 bg-card border border-border rounded-lg relative group">
                    <div className="font-semibold text-xs text-foreground mb-1">{note.title}</div>
                    <p className="text-[11px] text-muted-foreground italic whitespace-pre-wrap">{note.content}</p>
                    <div className="absolute right-2 top-2 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => {
                          setSelectedNote(note);
                          setNoteTitle(note.title);
                          setNoteContent(note.content);
                        }}
                        className="text-[10px] hover:text-primary font-bold"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => {
                          if (accessToken) deleteNote(accessToken, note.id);
                        }}
                        className="text-[10px] hover:text-destructive font-bold"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 3: Citation styles copy options */}
          {activeTab === "citations" && (
            <div className="space-y-4">
              <div className="flex flex-wrap gap-1.5">
                {(["apa", "ieee", "mla", "bibtex"] as const).map((style) => (
                  <button
                    key={style}
                    onClick={() => handleGenerateBibliography(style)}
                    className="text-[10px] uppercase font-bold px-2 py-1 bg-muted rounded hover:bg-primary hover:text-primary-foreground transition-all"
                  >
                    Format {style}
                  </button>
                ))}
              </div>

              <div className="space-y-2">
                <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                  Bibliography Output
                </h4>
                {bibliography.length === 0 ? (
                  <div className="text-xs text-muted-foreground italic">No citations formatted. Select format style.</div>
                ) : (
                  bibliography.map((ref, i) => (
                    <div key={i} className="p-2.5 bg-card border border-border rounded text-[11px] leading-relaxed relative group">
                      <span className="block text-foreground pr-6">{ref}</span>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(ref);
                        }}
                        className="absolute right-1 top-1 p-1 hover:bg-muted text-muted-foreground hover:text-primary rounded opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Copy to Clipboard"
                      >
                        <Clipboard className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Tab 4: Graph insights mapping */}
          {activeTab === "insights" && (
            <div className="space-y-4">
              <button
                onClick={handleLoadInsights}
                className="w-full text-xs py-2 bg-primary text-primary-foreground font-semibold rounded hover:bg-primary/95 transition-all flex items-center justify-center gap-1.5"
              >
                <Map className="w-4 h-4" />
                Generate Concept Mapping
              </button>

              {insights ? (
                <div className="space-y-3 text-xs">
                  <div>
                    <h4 className="font-bold text-muted-foreground uppercase tracking-wider text-[10px] mb-1.5">
                      Extracted Entities
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {insights.entities.map((e) => (
                        <span key={e} className="px-2 py-0.5 bg-primary/5 border border-primary/20 text-foreground text-[10px] rounded">
                          {e}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="font-bold text-muted-foreground uppercase tracking-wider text-[10px] mb-1.5">
                      Open Questions
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-muted-foreground text-[11px]">
                      {insights.open_questions.map((q, i) => (
                        <li key={i}>{q}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-muted-foreground italic">No concept map generated. Click build.</div>
              )}
            </div>
          )}
        </div>
      </aside>
    </div>
  );
};
