import React, { useState, useEffect, useCallback } from "react";
import { useAuthStore } from "../store/auth";
import { PasswordInput } from "../components/auth/PasswordInput";
import { SessionCard } from "../components/auth/SessionCard";
import { Save, ShieldAlert, KeyRound, MonitorSmartphone } from "lucide-react";

interface SessionData {
  id: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

export const Security: React.FC = () => {
  const { accessToken } = useAuthStore();
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = "http://localhost:8000/api/v1";

  const fetchSessions = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/users/sessions`, {
        headers: { "Authorization": `Bearer ${accessToken}` },
      });
      if (res.ok) {
        const data = await res.ok ? await res.json() : [];
        setSessions(data);
      }
    } catch (e) {
      // Silence fetch errors in scaffolding
    }
  }, [accessToken]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);

    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("Please fill in all password fields.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("New passwords credentials do not match.");
      return;
    }
    if (newPassword.length < 8) {
      setError("Password length must be at least 8 characters.");
      return;
    }

    setPasswordLoading(true);
    try {
      const res = await fetch(`${API_BASE}/users/password`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Incorrect old password verification.");
      }

      setMessage("Password updated successfully. Other active sessions revoked.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setPasswordLoading(false);
      // Refresh session list
      await fetchSessions();
    } catch (err: any) {
      setError(err.message || "Failed to update account password.");
      setPasswordLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/users/sessions/${sessionId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${accessToken}` },
      });
      if (res.ok) {
        // Refresh session list
        setSessions(prev => prev.filter(s => s.id !== sessionId));
      }
    } catch (e) {
      // Silence revocation failures
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6 md:p-10">
      <div className="max-w-4xl mx-auto flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
            Security Settings
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Secure your credentials, change password hashes, and manage active device sessions.
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Change Password Block */}
          <form onSubmit={handlePasswordUpdate} className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4 h-fit">
            <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
              <KeyRound className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                Change Password
              </h2>
            </div>

            <PasswordInput
              label="Current Password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="••••••••"
            />

            <PasswordInput
              label="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Min. 8 characters"
            />

            <PasswordInput
              label="Confirm New Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat new password"
            />

            <button
              type="submit"
              disabled={passwordLoading}
              className="mt-2 py-2 rounded-lg bg-indigo-500 text-white font-semibold text-sm hover:bg-indigo-600 transition-all outline-none disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {passwordLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Update Password</span>
                </>
              )}
            </button>
          </form>

          {/* Active Sessions Block */}
          <div className="rounded-2xl bg-slate-900 border border-slate-800 p-6 flex flex-col gap-4">
            <div className="flex items-center gap-2.5 pb-2 border-b border-slate-800/80">
              <MonitorSmartphone className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
                Active Devices
              </h2>
            </div>
            
            <p className="text-[11px] text-slate-500">
              You are currently signed in on these browser devices. Revoking a session will force a logout.
            </p>

            <div className="flex flex-col gap-3">
              {sessions.length === 0 ? (
                <div className="text-center py-6 text-slate-650 text-xs font-semibold">
                  No other active device sessions found.
                </div>
              ) : (
                sessions.map((session, index) => (
                  <SessionCard
                    key={session.id}
                    session={session}
                    isCurrent={index === 0} // Display first session as current mock
                    onRevoke={handleRevokeSession}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Security;
