import React, { useState } from "react";
import { Laptop, ShieldAlert, Trash2 } from "lucide-react";

interface SessionData {
  id: string;
  ip_address?: string;
  user_agent?: string;
  created_at: string;
}

interface SessionCardProps {
  session: SessionData;
  isCurrent?: boolean;
  onRevoke: (id: string) => Promise<void>;
}

export const SessionCard: React.FC<SessionCardProps> = ({ session, isCurrent = false, onRevoke }) => {
  const [revoking, setRevoking] = useState(false);

  const handleRevoke = async () => {
    setRevoking(true);
    try {
      await onRevoke(session.id);
    } catch (e) {
      setRevoking(false);
    }
  };

  const formattedDate = new Date(session.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });

  return (
    <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900 border border-slate-800 text-slate-100 font-sans shadow-sm transition-all hover:border-slate-700/80">
      <div className="flex items-start gap-3">
        <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-indigo-400 mt-0.5">
          <Laptop className="w-5 h-5" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold">
              {session.ip_address || "Unknown IP Location"}
            </span>
            {isCurrent && (
              <span className="px-2 py-0.5 text-[10px] font-medium tracking-wider uppercase bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full">
                Current
              </span>
            )}
          </div>
          <span className="text-xs text-slate-500 line-clamp-1 max-w-[280px] md:max-w-md mt-0.5">
            {session.user_agent || "Generic Browser Identity"}
          </span>
          <span className="text-[11px] text-slate-600 mt-1">
            Logged in on {formattedDate}
          </span>
        </div>
      </div>

      {!isCurrent && (
        <button
          onClick={handleRevoke}
          disabled={revoking}
          className="p-2 rounded-lg bg-slate-950 border border-slate-800/80 text-slate-400 hover:text-rose-400 hover:border-rose-900/40 hover:bg-rose-500/5 transition-all outline-none disabled:opacity-50"
          title="Revoke session credentials"
        >
          {revoking ? (
            <div className="w-4 h-4 border-2 border-rose-500 border-t-transparent rounded-full animate-spin" />
          ) : (
            <Trash2 className="w-4 h-4" />
          )}
        </button>
      )}
    </div>
  );
};
