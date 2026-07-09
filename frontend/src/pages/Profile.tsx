import React, { useState, useEffect } from "react";
import { useAuthStore } from "../store/auth";
import { Save, User, ShieldAlert, Sparkles, Sliders } from "lucide-react";

export const Profile: React.FC = () => {
  const { user, preferences, updateProfile, updatePreferences } = useAuthStore();
  const [email, setEmail] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [theme, setTheme] = useState("light");
  const [provider, setProvider] = useState("ollama");
  const [model, setModel] = useState("llama3.2:3b");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setEmail(user.email);
      setAvatarUrl(user.avatar_url || "");
    }
    if (preferences) {
      setTheme(preferences.theme);
      setProvider(preferences.default_provider);
      setModel(preferences.default_model);
    }
  }, [user, preferences]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      // Save Profile
      await updateProfile(email, avatarUrl || undefined);
      // Save Preferences
      await updatePreferences(theme, provider, model);
      
      setMessage("Workspace profile settings saved successfully.");
      setLoading(false);
    } catch (e: any) {
      setError(e.message || "Failed to update profile settings.");
      setLoading(false);
    }
  };

  const initials = user?.email.substring(0, 2).toUpperCase() || "US";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6 md:p-10">
      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Profile Settings
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Configure your personal profile settings and default AI Operating System properties.
          </p>
        </div>

        {message && (
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2.5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
            <ShieldAlert className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Card left: Avatar preview uploads */}
          <div className="md:col-span-1 rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col items-center justify-center text-center gap-4 h-fit">
            <div className="relative group">
              <div className="w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center text-white text-3xl font-bold shadow-lg border border-slate-850">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="Avatar" className="w-full h-full object-cover rounded-full" />
                ) : (
                  initials
                )}
              </div>
            </div>
            <div>
              <h3 className="text-sm font-bold">Your Avatar</h3>
              <p className="text-[11px] text-slate-500 mt-1">
                Enter an image URL below to update your picture initials.
              </p>
            </div>
            <input
              type="text"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              placeholder="https://example.com/image.png"
              className="w-full px-3 py-1.5 bg-slate-950 border border-slate-850 rounded-lg text-xs text-white placeholder-slate-600 outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          {/* Settings Content Fields */}
          <div className="md:col-span-2 flex flex-col gap-6">
            {/* Account Details Block */}
            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
                <User className="w-4 h-4 text-indigo-400" />
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                  Account Details
                </h2>
              </div>
              <div className="flex flex-col gap-1 w-full text-slate-100 font-sans">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-lg text-sm text-white placeholder-slate-600 outline-none transition-all"
                />
              </div>
            </div>

            {/* AI Preferences Manager Block */}
            <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
                <Sliders className="w-4 h-4 text-indigo-400" />
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                  Workspace Preferences
                </h2>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1 text-slate-100">
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Interface Theme
                  </label>
                  <select
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-lg text-sm text-white outline-none transition-all"
                  >
                    <option value="light">Light Mode</option>
                    <option value="dark">Dark Mode</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1 text-slate-100">
                  <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Default AI Provider
                  </label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-lg text-sm text-white outline-none transition-all"
                  >
                    <option value="ollama">Ollama (Offline)</option>
                    <option value="gemini">Google Gemini (Cloud)</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-col gap-1 text-slate-100">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Default AI LLM Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 focus:border-indigo-500 rounded-lg text-sm text-white outline-none transition-all"
                >
                  <option value="llama3.2:3b">llama3.2:3b (Standard offline)</option>
                  <option value="gemini-2.5-flash">gemini-2.5-flash (Standard cloud)</option>
                  <option value="gemini-2.5-pro">gemini-2.5-pro (Advanced coding)</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 self-end rounded-lg bg-indigo-500 text-white font-semibold text-sm hover:bg-indigo-600 transition-all outline-none disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Profile</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
export default Profile;
