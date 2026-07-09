import React, { useState, useEffect, useCallback } from "react";
import { useAuthStore } from "../store/auth";
import { useWorkspaceStore } from "../store/workspace";
import { 
  Cpu, Save, User, Activity, HardDrive, 
  Trash2, Mail, Plus, Briefcase, ChevronRight, Check
} from "lucide-react";

export const Settings: React.FC = () => {
  const { accessToken } = useAuthStore();
  const { 
    workspaces, activeWorkspace, members, storage, aiSettings, activities,
    createWorkspace, switchWorkspace, fetchMembers, fetchStorage, fetchAISettings,
    updateAISettings, fetchActivities, inviteMember, removeMember
  } = useWorkspaceStore();

  const [activeTab, setActiveTab] = useState<"general" | "members" | "ai" | "usage">("general");

  // General tab states
  const [newWsName, setNewWsName] = useState("");
  const [newWsDesc, setNewWsDesc] = useState("");
  const [createName, setCreateName] = useState("");
  const [createDesc, setCreateDesc] = useState("");

  // Members tab states
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("viewer");

  // AI settings states
  const [aiProvider, setAiProvider] = useState("ollama");
  const [aiModel, setAiModel] = useState("llama3.2:3b");
  const [aiTemp, setAiTemp] = useState(0.7);
  const [aiTokens, setAiTokens] = useState(2048);

  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Fetch all dependencies when workspace switches
  const loadWorkspaceData = useCallback(async () => {
    if (!accessToken || !activeWorkspace) return;
    await fetchMembers(accessToken, activeWorkspace.id);
    await fetchStorage(accessToken, activeWorkspace.id);
    await fetchAISettings(accessToken, activeWorkspace.id);
    await fetchActivities(accessToken, activeWorkspace.id);
  }, [accessToken, activeWorkspace, fetchMembers, fetchStorage, fetchAISettings, fetchActivities]);

  useEffect(() => {
    loadWorkspaceData();
  }, [loadWorkspaceData]);

  // Set form fields on load
  useEffect(() => {
    if (activeWorkspace) {
      setNewWsName(activeWorkspace.name);
      setNewWsDesc(activeWorkspace.description || "");
    }
    if (aiSettings) {
      setAiProvider(aiSettings.default_provider);
      setAiModel(aiSettings.default_model);
      setAiTemp(aiSettings.temperature);
      setAiTokens(aiSettings.max_tokens);
    }
  }, [activeWorkspace, aiSettings]);

  const handleCreateWorkspace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createName || !accessToken) return;
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      await createWorkspace(accessToken, createName, createDesc);
      setCreateName("");
      setCreateDesc("");
      setMessage("Workspace created successfully.");
    } catch (e: any) {
      setError(e.message || "Failed to create workspace.");
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail || !accessToken || !activeWorkspace) return;
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      await inviteMember(accessToken, activeWorkspace.id, inviteEmail, inviteRole);
      setInviteEmail("");
      setMessage(`Invitation sent to ${inviteEmail}.`);
    } catch (e: any) {
      setError(e.message || "Failed to send invitation.");
    } finally {
      setLoading(false);
    }
  };

  const handleAISave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !activeWorkspace) return;
    setLoading(true);
    setMessage(null);
    setError(null);
    try {
      await updateAISettings(
        accessToken, 
        activeWorkspace.id, 
        aiProvider, 
        aiModel, 
        aiTemp, 
        aiTokens
      );
      setMessage("Workspace independent AI parameters updated.");
    } catch (e: any) {
      setError(e.message || "Failed to update AI settings.");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveMember = async (userId: string) => {
    if (!accessToken || !activeWorkspace) return;
    await removeMember(accessToken, activeWorkspace.id, userId);
  };

  return (
    <div className="min-h-screen text-slate-100 font-sans p-6 md:p-10 text-left">
      <div className="max-w-6xl mx-auto flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Workspace Configuration
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage multi-tenant organizations, invite workspace members, override AI models, and review activity audits.
          </p>
        </div>

        {message && (
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            {message}
          </div>
        )}

        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Settings Sidebar Tabs */}
          <div className="md:col-span-1 flex flex-col gap-1.5">
            <button
              onClick={() => { setActiveTab("general"); setMessage(null); setError(null); }}
              className={`flex items-center gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors text-left ${
                activeTab === "general" ? "bg-slate-900 text-indigo-400 border border-slate-800" : "text-slate-400 hover:bg-slate-900/40 hover:text-slate-200"
              }`}
            >
              <Briefcase className="w-4 h-4" />
              <span>General Settings</span>
            </button>
            <button
              onClick={() => { setActiveTab("members"); setMessage(null); setError(null); }}
              className={`flex items-center gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors text-left ${
                activeTab === "members" ? "bg-slate-900 text-indigo-400 border border-slate-800" : "text-slate-400 hover:bg-slate-900/40 hover:text-slate-200"
              }`}
            >
              <User className="w-4 h-4" />
              <span>Workspace Members</span>
            </button>
            <button
              onClick={() => { setActiveTab("ai"); setMessage(null); setError(null); }}
              className={`flex items-center gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors text-left ${
                activeTab === "ai" ? "bg-slate-900 text-indigo-400 border border-slate-800" : "text-slate-400 hover:bg-slate-900/40 hover:text-slate-200"
              }`}
            >
              <Cpu className="w-4 h-4" />
              <span>AI Configuration</span>
            </button>
            <button
              onClick={() => { setActiveTab("usage"); setMessage(null); setError(null); }}
              className={`flex items-center gap-2.5 px-3 py-2 text-xs font-semibold rounded-lg transition-colors text-left ${
                activeTab === "usage" ? "bg-slate-900 text-indigo-400 border border-slate-800" : "text-slate-400 hover:bg-slate-900/40 hover:text-slate-200"
              }`}
            >
              <HardDrive className="w-4 h-4" />
              <span>Storage & Activity</span>
            </button>
          </div>

          {/* Settings Tab Content */}
          <div className="md:col-span-3 flex flex-col gap-6">
            {/* General Tab */}
            {activeTab === "general" && (
              <div className="flex flex-col gap-6">
                <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
                  <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                    Create New Workspace
                  </h3>
                  <form onSubmit={handleCreateWorkspace} className="flex flex-col gap-3">
                    <div className="flex flex-col gap-1">
                      <label className="text-[10px] font-bold text-slate-400 uppercase">Workspace Name</label>
                      <input
                        type="text"
                        value={createName}
                        onChange={(e) => setCreateName(e.target.value)}
                        placeholder="e.g. Research Lab, Legal Department"
                        className="w-full px-3 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white placeholder-slate-700 outline-none focus:border-indigo-500 transition-colors"
                      />
                    </div>
                    <div className="flex flex-col gap-1">
                      <label className="text-[10px] font-bold text-slate-400 uppercase">Description</label>
                      <input
                        type="text"
                        value={createDesc}
                        onChange={(e) => setCreateDesc(e.target.value)}
                        placeholder="Brief summary explaining what this workspace holds..."
                        className="w-full px-3 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white placeholder-slate-700 outline-none focus:border-indigo-500 transition-colors"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="px-4 py-2 self-end rounded-lg bg-indigo-500 text-white font-semibold text-xs hover:bg-indigo-600 transition-colors flex items-center gap-1.5"
                    >
                      <Plus className="w-3.5 h-3.5" />
                      Create Workspace
                    </button>
                  </form>
                </div>
              </div>
            )}

            {/* Members Tab */}
            {activeTab === "members" && (
              <div className="flex flex-col gap-6">
                <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
                  <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                    Invite Member
                  </h3>
                  <form onSubmit={handleInvite} className="flex gap-3">
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="teammate@company.com"
                      className="flex-1 px-3 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white placeholder-slate-700 outline-none focus:border-indigo-500 transition-colors"
                    />
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value)}
                      className="px-3 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white outline-none"
                    >
                      <option value="viewer">Viewer</option>
                      <option value="editor">Editor</option>
                      <option value="administrator">Administrator</option>
                    </select>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-indigo-500 text-white font-semibold text-xs rounded-lg hover:bg-indigo-600 transition-colors flex items-center gap-1.5"
                    >
                      <Mail className="w-3.5 h-3.5" /> Invite
                    </button>
                  </form>
                </div>

                <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
                  <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                    Active Seating
                  </h3>
                  <div className="flex flex-col gap-3">
                    {members.map((m) => (
                      <div key={m.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-950/80 border border-slate-850 text-xs">
                        <div className="flex flex-col">
                          <span className="font-semibold text-slate-200">{m.email || "Active seat user"}</span>
                          <span className="text-[10px] text-slate-500 mt-0.5">Joined on {new Date(m.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="px-2 py-0.5 text-[9px] font-bold tracking-wider uppercase border border-slate-800 bg-slate-900 text-slate-400 rounded-full">
                            {m.role_name}
                          </span>
                          {m.role_name !== "owner" && (
                            <button
                              onClick={() => handleRemoveMember(m.user_id)}
                              className="p-1.5 text-slate-500 hover:text-rose-400 transition-colors"
                              title="Revoke access"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* AI Configuration Tab */}
            {activeTab === "ai" && (
              <form onSubmit={handleAISave} className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
                <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                  Independent AI Config overrides
                </h3>
                <p className="text-[11px] text-slate-500">
                  Settings modified here will override system default routing parameters for any agent runs inside this workspace.
                </p>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Default LLM Provider</label>
                    <select
                      value={aiProvider}
                      onChange={(e) => setAiProvider(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white outline-none"
                    >
                      <option value="ollama">Ollama (Offline)</option>
                      <option value="gemini">Google Gemini (Cloud)</option>
                    </select>
                  </div>
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Default Model</label>
                    <select
                      value={aiModel}
                      onChange={(e) => setAiModel(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white outline-none"
                    >
                      <option value="llama3.2:3b">llama3.2:3b (Standard offline)</option>
                      <option value="gemini-2.5-flash">gemini-2.5-flash (Standard cloud)</option>
                      <option value="gemini-2.5-pro">gemini-2.5-pro (Advanced coding)</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Temperature ({aiTemp})</label>
                    <input
                      type="range"
                      min="0.0"
                      max="1.2"
                      step="0.1"
                      value={aiTemp}
                      onChange={(e) => setAiTemp(parseFloat(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                  </div>
                  <div className="flex flex-col gap-1">
                    <label className="text-[10px] font-bold text-slate-400 uppercase">Max Tokens ({aiTokens})</label>
                    <input
                      type="number"
                      value={aiTokens}
                      onChange={(e) => setAiTokens(parseInt(e.target.value))}
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white outline-none"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 self-end rounded-lg bg-indigo-500 text-white font-semibold text-xs hover:bg-indigo-600 transition-colors flex items-center gap-1.5"
                >
                  <Save className="w-3.5 h-3.5" /> Save Overrides
                </button>
              </form>
            )}

            {/* Storage & Activity Tab */}
            {activeTab === "usage" && (
              <div className="flex flex-col gap-6">
                {/* Storage Card */}
                {storage && (
                  <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
                    <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                      Workspace Storage Usage
                    </h3>
                    <div>
                      <div className="flex justify-between text-xs font-semibold text-slate-300 mb-1.5">
                        <span>{(storage.bytes_used / (1024 * 1024)).toFixed(2)} MB used</span>
                        <span>{(storage.bytes_quota / (1024 * 1024 * 1024)).toFixed(0)} GB Quota</span>
                      </div>
                      <div className="w-full bg-slate-950 rounded-full h-2 border border-slate-850 overflow-hidden">
                        <div 
                          className="bg-indigo-500 h-full transition-all duration-350"
                          style={{ width: `${(storage.bytes_used / storage.bytes_quota) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Activity Feed */}
                <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
                  <h3 className="text-sm font-bold tracking-wider text-slate-400 uppercase">
                    Workspace Audit Activity Logs
                  </h3>
                  <div className="flex flex-col gap-2.5 max-h-[300px] overflow-y-auto pr-1">
                    {activities.length === 0 ? (
                      <div className="text-center py-6 text-slate-600 text-xs font-semibold">
                        No activity records found.
                      </div>
                    ) : (
                      activities.map((a) => (
                        <div key={a.id} className="p-3 rounded-lg bg-slate-950/80 border border-slate-850 flex items-start gap-2.5 text-xs">
                          <Activity className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                          <div className="flex flex-col text-left">
                            <span className="font-semibold text-slate-200">
                              {a.action.replace(/_/g, " ")}
                            </span>
                            <span className="text-[10px] text-slate-500">
                              Logged by {a.email || a.user_id} on {new Date(a.created_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
export default Settings;
