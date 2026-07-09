import { create } from "zustand";

export interface Project {
  id: string;
  workspace_id: string;
  name: string;
  description?: string;
  color: string;
  icon: string;
  is_archived: boolean;
  created_at: string;
}

export interface Collection {
  id: string;
  project_id: string;
  workspace_id: string;
  name: string;
  description?: string;
  color: string;
  icon: string;
  is_archived: boolean;
  created_at: string;
}

export interface Folder {
  id: string;
  collection_id: string;
  parent_id?: string;
  workspace_id: string;
  name: string;
  color: string;
  icon: string;
  is_archived: boolean;
  created_at: string;
}

export interface KnowledgeAsset {
  id: string;
  folder_id?: string;
  collection_id?: string;
  project_id?: string;
  workspace_id: string;
  name: string;
  asset_type: string;
  details: Record<string, any>;
  created_at: string;
}

export interface Favorite {
  id: string;
  user_id: string;
  workspace_id: string;
  target_id: string;
  target_type: string;
  created_at: string;
}

export interface RecycleItem {
  id: string;
  workspace_id: string;
  item_id: string;
  item_type: string;
  original_parent_id?: string;
  deleted_by: string;
  deleted_at: string;
}

export interface TimelineEvent {
  id: string;
  workspace_id: string;
  target_id: string;
  target_type: string;
  user_id: string;
  action: string;
  created_at: string;
}

export interface Tag {
  id: string;
  workspace_id: string;
  name: string;
  color: string;
}

interface KnowledgeState {
  projects: Project[];
  collections: Collection[];
  folders: Folder[];
  assets: KnowledgeAsset[];
  favorites: Favorite[];
  recycleBin: RecycleItem[];
  timeline: TimelineEvent[];
  tags: Tag[];
  activeProject: Project | null;
  activeCollection: Collection | null;
  activeFolder: Folder | null;
  loading: boolean;

  fetchProjects: (token: string, wsId: string) => Promise<void>;
  createProject: (token: string, wsId: string, name: string, description?: string) => Promise<Project>;
  fetchCollections: (token: string, projId: string) => Promise<void>;
  createCollection: (token: string, projId: string, wsId: string, name: string, description?: string) => Promise<Collection>;
  fetchFolders: (token: string, colId: string, parentId?: string) => Promise<void>;
  createFolder: (token: string, colId: string, wsId: string, name: string, parentId?: string) => Promise<Folder>;
  moveFolder: (token: string, folderId: string, newParentId: string | null) => Promise<void>;
  fetchAssets: (token: string, wsId: string, folderId?: string) => Promise<void>;
  createAsset: (token: string, wsId: string, name: string, type: string, folderId?: string, details?: Record<string, any>) => Promise<KnowledgeAsset>;
  deleteAsset: (token: string, wsId: string, assetId: string) => Promise<void>;
  fetchRecycleBin: (token: string, wsId: string) => Promise<void>;
  restoreItem: (token: string, wsId: string, itemId: string) => Promise<void>;
  permanentDeleteItem: (token: string, wsId: string, itemId: string) => Promise<void>;
  fetchFavorites: (token: string, wsId: string) => Promise<void>;
  toggleFavorite: (token: string, wsId: string, targetId: string, targetType: string) => Promise<void>;
  fetchTimeline: (token: string, wsId: string) => Promise<void>;
  fetchTags: (token: string, wsId: string) => Promise<void>;
  createTag: (token: string, wsId: string, name: string, color: string) => Promise<Tag>;
  setActiveProject: (proj: Project | null) => void;
  setActiveCollection: (col: Collection | null) => void;
  setActiveFolder: (f: Folder | null) => void;
}

const API_BASE = "http://localhost:8000/api/v1";

export const useKnowledgeStore = create<KnowledgeState>((set, get) => ({
  projects: [],
  collections: [],
  folders: [],
  assets: [],
  favorites: [],
  recycleBin: [],
  timeline: [],
  tags: [],
  activeProject: null,
  activeCollection: null,
  activeFolder: null,
  loading: false,

  fetchProjects: async (token, wsId) => {
    set({ loading: true });
    try {
      const res = await fetch(`${API_BASE}/knowledge/projects?workspace_id=${wsId}`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const list = await res.json();
        set({ projects: list, loading: false });
        if (list.length > 0 && !get().activeProject) {
          set({ activeProject: list[0] });
        }
      } else {
        set({ loading: false });
      }
    } catch (e) {
      set({ loading: false });
    }
  },

  createProject: async (token, wsId, name, description) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/projects`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ workspace_id: wsId, name, description }),
      });
      if (!res.ok) throw new Error("Failed to create project.");
      const data = await res.json();
      set((state) => ({ projects: [data, ...state.projects], activeProject: data }));
      return data;
    } catch (e) {
      throw e;
    }
  },

  fetchCollections: async (token, projId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/projects/${projId}/collections`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        const list = await res.json();
        set({ collections: list });
        if (list.length > 0 && !get().activeCollection) {
          set({ activeCollection: list[0] });
        }
      }
    } catch (e) {}
  },

  createCollection: async (token, projId, wsId, name, description) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/projects/${projId}/collections`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ workspace_id: wsId, name, description }),
      });
      if (!res.ok) throw new Error("Failed to create collection.");
      const data = await res.json();
      set((state) => ({ collections: [data, ...state.collections], activeCollection: data }));
      return data;
    } catch (e) {
      throw e;
    }
  },

  fetchFolders: async (token, colId, parentId) => {
    try {
      const url = parentId 
        ? `${API_BASE}/knowledge/collections/${colId}/folders?parent_id=${parentId}`
        : `${API_BASE}/knowledge/collections/${colId}/folders`;
      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set({ folders: await res.json() });
      }
    } catch (e) {}
  },

  createFolder: async (token, colId, wsId, name, parentId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/collections/${colId}/folders`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ workspace_id: wsId, name, parent_id: parentId }),
      });
      if (!res.ok) throw new Error("Failed to create folder.");
      const data = await res.json();
      set((state) => ({ folders: [...state.folders, data] }));
      return data;
    } catch (e) {
      throw e;
    }
  },

  moveFolder: async (token, folderId, newParentId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/folders/${folderId}/move`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ parent_id: newParentId }),
      });
      if (res.ok) {
        const data = await res.json();
        set((state) => ({
          folders: state.folders.map((f) => (f.id === folderId ? data : f)),
        }));
      }
    } catch (e) {}
  },

  fetchAssets: async (token, wsId, folderId) => {
    try {
      const url = folderId
        ? `${API_BASE}/knowledge/assets?workspace_id=${wsId}&folder_id=${folderId}`
        : `${API_BASE}/knowledge/assets?workspace_id=${wsId}`;
      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set({ assets: await res.json() });
      }
    } catch (e) {}
  },

  createAsset: async (token, wsId, name, type, folderId, details) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/assets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ workspace_id: wsId, name, asset_type: type, folder_id: folderId, details }),
      });
      if (!res.ok) throw new Error("Failed to create asset.");
      const data = await res.json();
      set((state) => ({ assets: [data, ...state.assets] }));
      return data;
    } catch (e) {
      throw e;
    }
  },

  deleteAsset: async (token, wsId, assetId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/assets/${assetId}?workspace_id=${wsId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set((state) => ({
          assets: state.assets.filter((a) => a.id !== assetId),
        }));
      }
    } catch (e) {}
  },

  fetchRecycleBin: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/recycle-bin?workspace_id=${wsId}`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set({ recycleBin: await res.json() });
      }
    } catch (e) {}
  },

  restoreItem: async (token, wsId, itemId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/recycle-bin/${itemId}/restore?workspace_id=${wsId}`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set((state) => ({
          recycleBin: state.recycleBin.filter((r) => r.item_id !== itemId),
        }));
      }
    } catch (e) {}
  },

  permanentDeleteItem: async (token, wsId, itemId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/recycle-bin/${itemId}?workspace_id=${wsId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set((state) => ({
          recycleBin: state.recycleBin.filter((r) => r.item_id !== itemId),
        }));
      }
    } catch (e) {}
  },

  fetchFavorites: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/favorites?workspace_id=${wsId}`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set({ favorites: await res.json() });
      }
    } catch (e) {}
  },

  toggleFavorite: async (token, wsId, targetId, targetType) => {
    try {
      const isFav = get().favorites.some((f) => f.target_id === targetId);
      if (isFav) {
        const res = await fetch(`${API_BASE}/knowledge/favorites/${targetId}?workspace_id=${wsId}`, {
          method: "DELETE",
          headers: { "Authorization": `Bearer ${token}` },
        });
        if (res.ok) {
          set((state) => ({
            favorites: state.favorites.filter((f) => f.target_id !== targetId),
          }));
        }
      } else {
        const res = await fetch(`${API_BASE}/knowledge/favorites`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
          body: JSON.stringify({ workspace_id: wsId, target_id: targetId, target_type: targetType }),
        });
        if (res.ok) {
          const data = await res.json();
          set((state) => ({ favorites: [...state.favorites, data] }));
        }
      }
    } catch (e) {}
  },

  fetchTimeline: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/timeline?workspace_id=${wsId}`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set({ timeline: await res.json() });
      }
    } catch (e) {}
  },

  fetchTags: async (token, wsId) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/tags?workspace_id=${wsId}`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (res.ok) {
        set({ tags: await res.json() });
      }
    } catch (e) {}
  },

  createTag: async (token, wsId, name, color) => {
    try {
      const res = await fetch(`${API_BASE}/knowledge/tags`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ workspace_id: wsId, name, color }),
      });
      if (!res.ok) throw new Error("Failed to create tag.");
      const data = await res.json();
      set((state) => ({ tags: [...state.tags, data] }));
      return data;
    } catch (e) {
      throw e;
    }
  },

  setActiveProject: (proj) => set({ activeProject: proj }),
  setActiveCollection: (col) => set({ activeCollection: col }),
  setActiveFolder: (f) => set({ activeFolder: f }),
}));
