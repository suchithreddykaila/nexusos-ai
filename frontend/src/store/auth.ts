import { create } from "zustand";

export interface UserProfile {
  id: string;
  email: string;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string | null;
}

export interface UserPreferences {
  theme: string;
  default_provider: string;
  default_model: string;
  custom_settings: Record<string, any>;
}

interface AuthState {
  user: UserProfile | null;
  preferences: UserPreferences | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  silentRefresh: () => Promise<void>;
  updateProfile: (email?: string, avatarUrl?: string) => Promise<void>;
  updatePreferences: (theme: string, provider: string, model: string) => Promise<void>;
}

const API_BASE = "http://localhost:8000/api/v1";

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  preferences: null,
  accessToken: null,
  isAuthenticated: false,
  loading: false,

  login: async (email, password) => {
    set({ loading: true });
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Authentication credentials failed.");
      }
      const data = await response.json();
      
      set({
        user: data.user,
        accessToken: data.access_token,
        isAuthenticated: true,
        loading: false,
      });

      // Load user preferences dynamically after login
      await get().checkAuth();
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  register: async (email, password) => {
    set({ loading: true });
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Registration processing failed.");
      }
      set({ loading: false });
    } catch (error) {
      set({ loading: false });
      throw error;
    }
  },

  logout: async () => {
    const token = get().accessToken;
    try {
      await fetch(`${API_BASE}/auth/logout`, {
        method: "POST",
        headers: token ? { "Authorization": `Bearer ${token}` } : {},
      });
    } catch (e) {
      // Allow frontend logout even if backend revoke fails
    } finally {
      set({
        user: null,
        preferences: null,
        accessToken: null,
        isAuthenticated: false,
      });
    }
  },

  checkAuth: async () => {
    const token = get().accessToken;
    if (!token) return;

    try {
      // Get Profile details
      const profileRes = await fetch(`${API_BASE}/auth/me`, {
        headers: { "Authorization": `Bearer ${token}` },
      });
      if (profileRes.ok) {
        const user = await profileRes.json();
        set({ user, isAuthenticated: true });

        // Get preferences details
        const prefRes = await fetch(`${API_BASE}/users/preferences`, {
          headers: { "Authorization": `Bearer ${token}` },
        });
        if (prefRes.ok) {
          const preferences = await prefRes.json();
          set({ preferences });
        }
      } else {
        // Access token expired, attempt silent token refresh
        await get().silentRefresh();
      }
    } catch (e) {
      set({ isAuthenticated: false, user: null, accessToken: null });
    }
  },

  silentRefresh: async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        set({ accessToken: data.access_token, isAuthenticated: true });
        await get().checkAuth();
      } else {
        set({ isAuthenticated: false, user: null, accessToken: null });
      }
    } catch (e) {
      set({ isAuthenticated: false, user: null, accessToken: null });
    }
  },

  updateProfile: async (email, avatarUrl) => {
    const token = get().accessToken;
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/users/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ email, avatar_url: avatarUrl }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Profile update failed.");
      }
      const data = await response.json();
      set({ user: data });
    } catch (e) {
      throw e;
    }
  },

  updatePreferences: async (theme, provider, model) => {
    const token = get().accessToken;
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE}/users/preferences`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          theme,
          default_provider: provider,
          default_model: model,
        }),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Preferences update failed.");
      }
      const data = await response.json();
      set({ preferences: data });
      
      // Enforce theme change in UI html element
      const root = window.document.documentElement;
      if (theme === "dark") {
        root.classList.add("dark");
      } else {
        root.classList.remove("dark");
      }
    } catch (e) {
      throw e;
    }
  },
}));
