import { create } from "zustand";

export interface ResearchSession {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  asset_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface ResearchNote {
  id: string;
  session_id: string;
  title: string;
  content: string;
  linked_asset_ids: string[];
  created_at: string;
  updated_at: string;
}

interface ResearchState {
  sessions: ResearchSession[];
  activeSession: ResearchSession | null;
  notes: ResearchNote[];
  bibliography: string[];
  insights: { entities: string[]; relationships: any[]; open_questions: string[] } | null;
  loading: boolean;
  
  fetchSessions: (token: string, wsId: string) => Promise<void>;
  createSession: (token: string, wsId: string, name: string, description?: string, assetIds?: string[]) => Promise<ResearchSession>;
  fetchSession: (token: string, id: string) => Promise<void>;
  fetchNotes: (token: string, sessionId: string) => Promise<void>;
  createNote: (token: string, sessionId: string, title: string, content: string, linkedAssetIds?: string[]) => Promise<ResearchNote>;
  updateNote: (token: string, noteId: string, title?: string, content?: string, linkedAssetIds?: string[]) => Promise<ResearchNote>;
  deleteNote: (token: string, noteId: string) => Promise<void>;
  generateCitations: (token: string, assetIds: string[], style: string) => Promise<void>;
  fetchInsights: (token: string, assetIds: string[]) => Promise<void>;
  setActiveSession: (session: ResearchSession | null) => void;
}

const API_BASE = "http://localhost:8000/api/v1/research";

export const useResearchStore = create<ResearchState>((set, get) => ({
  sessions: [],
  activeSession: null,
  notes: [],
  bibliography: [],
  insights: null,
  loading: false,

  setActiveSession: (session) => set({ activeSession: session }),

  fetchSessions: async (token, wsId) => {
    set({ loading: true });
    try {
      // Mock retrieve active sessions or list them
      const response = await fetch(`${API_BASE}/session/mock_list?workspace_id=${wsId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        set({ sessions: data });
      } else {
        // Fallback placeholder lists for UI demo
        set({
          sessions: [
            {
              id: "sess_1", workspace_id: wsId, name: "Deep Learning Architectures",
              description: "Analysis of Neural Networks and Transformers", asset_ids: [],
              created_at: new Date().toISOString(), updated_at: new Date().toISOString()
            }
          ]
        });
      }
    } catch (e) {
      // Set baseline default placeholder
      set({
        sessions: [
          {
            id: "sess_1", workspace_id: wsId, name: "Deep Learning Architectures",
            description: "Analysis of Neural Networks and Transformers", asset_ids: [],
            created_at: new Date().toISOString(), updated_at: new Date().toISOString()
          }
        ]
      });
    } finally {
      set({ loading: false });
    }
  },

  createSession: async (token, wsId, name, description, assetIds) => {
    set({ loading: true });
    try {
      const response = await fetch(`${API_BASE}/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ workspace_id: wsId, name, description, asset_ids: assetIds || [] })
      });
      if (!response.ok) throw new Error("Failed to create study session.");
      const data = await response.json();
      set((state) => ({ sessions: [data, ...state.sessions], activeSession: data }));
      return data;
    } catch (e) {
      const fallback: ResearchSession = {
        id: `sess_${Math.random().toString(36).substring(7)}`,
        workspace_id: wsId, name, description, asset_ids: assetIds || [],
        created_at: new Date().toISOString(), updated_at: new Date().toISOString()
      };
      set((state) => ({ sessions: [fallback, ...state.sessions], activeSession: fallback }));
      return fallback;
    } finally {
      set({ loading: false });
    }
  },

  fetchSession: async (token, id) => {
    set({ loading: true });
    try {
      const response = await fetch(`${API_BASE}/session/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        set({ activeSession: data });
      }
    } catch (e) {
      console.error(e);
    } finally {
      set({ loading: false });
    }
  },

  fetchNotes: async (token, sessionId) => {
    try {
      const response = await fetch(`${API_BASE}/session/${sessionId}/notes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        set({ notes: data });
      }
    } catch (e) {
      console.error(e);
    }
  },

  createNote: async (token, sessionId, title, content, linkedAssetIds) => {
    try {
      const response = await fetch(`${API_BASE}/notes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: sessionId, title, content, linked_asset_ids: linkedAssetIds || [] })
      });
      const data = await response.json();
      set((state) => ({ notes: [...state.notes, data] }));
      return data;
    } catch (e) {
      const fallback: ResearchNote = {
        id: `note_${Math.random().toString(36).substring(7)}`,
        session_id: sessionId, title, content, linked_asset_ids: linkedAssetIds || [],
        created_at: new Date().toISOString(), updated_at: new Date().toISOString()
      };
      set((state) => ({ notes: [...state.notes, fallback] }));
      return fallback;
    }
  },

  updateNote: async (token, noteId, title, content, linkedAssetIds) => {
    try {
      const response = await fetch(`${API_BASE}/notes/${noteId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: get().activeSession?.id || "", title: title || "", content: content || "", linked_asset_ids: linkedAssetIds || [] })
      });
      const data = await response.json();
      set((state) => ({
        notes: state.notes.map((n) => (n.id === noteId ? data : n))
      }));
      return data;
    } catch (e) {
      const target = get().notes.find((n) => n.id === noteId);
      const fallback: ResearchNote = {
        id: noteId,
        session_id: get().activeSession?.id || "",
        title: title !== undefined ? title : (target?.title || "Note"),
        content: content !== undefined ? content : (target?.content || ""),
        linked_asset_ids: linkedAssetIds !== undefined ? linkedAssetIds : (target?.linked_asset_ids || []),
        created_at: target?.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      set((state) => ({
        notes: state.notes.map((n) => (n.id === noteId ? fallback : n))
      }));
      return fallback;
    }
  },

  deleteNote: async (token, noteId) => {
    try {
      await fetch(`${API_BASE}/notes/${noteId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      set((state) => ({ notes: state.notes.filter((n) => n.id !== noteId) }));
    } catch (e) {
      set((state) => ({ notes: state.notes.filter((n) => n.id !== noteId) }));
    }
  },

  generateCitations: async (token, assetIds, style) => {
    try {
      const response = await fetch(`${API_BASE}/citations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ asset_ids: assetIds, style })
      });
      if (response.ok) {
        const data = await response.json();
        set({ bibliography: data });
      }
    } catch (e) {
      console.error(e);
    }
  },

  fetchInsights: async (token, assetIds) => {
    try {
      const response = await fetch(`${API_BASE}/insights`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ asset_ids: assetIds })
      });
      if (response.ok) {
        const data = await response.json();
        set({ insights: data });
      }
    } catch (e) {
      console.error(e);
    }
  }
}));
