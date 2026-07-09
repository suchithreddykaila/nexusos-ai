import { create } from "zustand";

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  logo_url?: string;
  color_theme: string;
  icon: string;
  is_archived: boolean;
}

export interface WorkspaceMember {
  id: string;
  workspace_id: string;
  user_id: string;
  email?: string;
  role_name: string;
  created_at: string;
}

export interface WorkspaceStorage {
  workspace_id: string;
  bytes_used: number;
  bytes_quota: number;
}

export interface WorkspaceAISettings {
  workspace_id: string;
  default_provider: string;
  default_model: string;
  temperature: number;
  max_tokens: number;
}

export interface WorkspaceActivity {
  id: string;
  user_id: string;
  email?: string;
  action: string;
  details: Record<string, any>;
  created_at: string;
}

interface WorkspaceState {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  members: WorkspaceMember[];
  storage: WorkspaceStorage | null;
  aiSettings: WorkspaceAISettings | null;
  activities: WorkspaceActivity[];
  loading: boolean;

  fetchWorkspaces: (token: string) => Promise<void>;
  createWorkspace: (token: string, name: string, description?: string) => Promise<Workspace>;
  switchWorkspace: (token: string, wsId: string) => Promise<void>;
  fetchMembers: (token: string, wsId: string) => Promise<void>;
  fetchStorage: (token: string, wsId: string) => Promise<void>;
  fetchAISettings: (token: string, wsId: string) => Promise<void>;
  updateAISettings: (token: string, wsId: string, provider: string, model: string, temp: number, tokens: number) => Promise<void>;
  fetchActivities: (token: string, wsId: string) => Promise<void>;
  inviteMember: (token: string, wsId: string, email: string, role: string) => Promise<void>;
  removeMember: (token: string, wsId: string, userId: string) => Promise<void>;
}

const API_BASE = "http://localhost:8000/api/v1";

export const useWorkspaceStore = create<WorkspaceState>((set, get) => ({
  workspaces: [],
  activeWorkspace: null,
  members: [],
  storage: null,
  aiSettings: null,
  activities: [],
  loading: false,

  fetchWorkspaces: async (token) => {
    set({ loading: true });
    try {
      const res = await fetch(`${API_BASE}/workspaces`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const list = await res.json();
        set({ workspaces: list, loading: false });
        if (list.length > 0 && !get().activeWorkspace) {
          set({ activeWorkspace: list[0] });
        }
      } else {
        set({ loading: false });
      }
    } catch (e) {
      set({ loading: false });
    }
  },

  createWorkspace: async (token, name, description) => {
    set({ loading: true });
    try {
      const res = await fetch(`${API_BASE}/workspaces`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ name, description }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to create workspace.");
      }
      const data = await res.json();
      set((state) => ({
        workspaces: [data, ...state.workspaces],
        activeWorkspace: data,
        loading: false,
      }));
      return data;
    } catch (e) {
      set({ loading: false });
      throw e;
    }
  },

  switchWorkspace: async (token, wsId) => {
    set({ loading: true });
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/switch`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        set({ activeWorkspace: data, loading: false });
        
        // Refresh workspace settings
        await get().fetchMembers(token, wsId);
        await get().fetchStorage(token, wsId);
        await get().fetchAISettings(token, wsId);
      } else {
        set({ loading: false });
      }
    } catch (e) {
      set({ loading: false });
    }
  },

  fetchMembers: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/members`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const list = await res.json();
        set({ members: list });
      }
    } catch (e) {}
  },

  fetchStorage: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/storage`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        set({ storage: data });
      }
    } catch (e) {}
  },

  fetchAISettings: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/ai`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        set({ aiSettings: data });
      }
    } catch (e) {}
  },

  updateAISettings: async (token, wsId, provider, model, temp, tokens) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/ai`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          default_provider: provider,
          default_model: model,
          temperature: temp,
          max_tokens: tokens,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        set({ aiSettings: data });
      } else {
        const err = await res.json();
        throw new Error(err.detail || "Failed to update AI settings.");
      }
    } catch (e) {
      throw e;
    }
  },

  fetchActivities: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/activity`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const list = await res.json();
        set({ activities: list });
      }
    } catch (e) {}
  },

  inviteMember: async (token, wsId, email, role) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/invite`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ email, role_name: role }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to send invitation.");
      }
    } catch (e) {
      throw e;
    }
  },

  removeMember: async (token, wsId, userId) => {
    try {
      const res = await fetch(`${API_BASE}/workspaces/${wsId}/members/${userId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set((state) => ({
          members: state.members.filter((m) => m.user_id !== userId),
        }));
      }
    } catch (e) {}
  },
}));
