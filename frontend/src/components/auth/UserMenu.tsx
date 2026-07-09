import React, { useState, useRef, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/auth";
import { LogOut, Settings, Shield, User, ChevronDown } from "lucide-react";

export const UserMenu: React.FC = () => {
  const { user, logout } = useAuthStore();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  if (!user) return null;

  const initials = user.email.substring(0, 2).toUpperCase();

  const handleLogout = async () => {
    setOpen(false);
    await logout();
    navigate("/login");
  };

  return (
    <div className="relative font-sans text-slate-100" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 p-1.5 rounded-lg bg-slate-900 border border-slate-800/80 hover:bg-slate-850 hover:border-slate-700 transition-all outline-none"
      >
        <div className="w-7 h-7 rounded-md bg-gradient-to-tr from-indigo-500 to-violet-500 text-white font-bold text-xs flex items-center justify-center shadow-md">
          {user.avatar_url ? (
            <img src={user.avatar_url} alt="Profile" className="w-full h-full object-cover rounded-md" />
          ) : (
            initials
          )}
        </div>
        <span className="text-xs font-semibold max-w-[100px] truncate hidden md:inline">
          {user.email}
        </span>
        <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl bg-slate-950/90 border border-slate-850 shadow-2xl backdrop-blur-xl py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="px-4 py-2 border-b border-slate-900">
            <span className="block text-xs font-semibold uppercase tracking-wider text-slate-500">
              Signed in as
            </span>
            <span className="block text-xs font-medium text-slate-300 truncate mt-0.5">
              {user.email}
            </span>
          </div>

          <div className="p-1 flex flex-col gap-0.5">
            <Link
              to="/profile"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <User className="w-4 h-4 text-slate-500" />
              <span>Profile Settings</span>
            </Link>

            <Link
              to="/security"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <Shield className="w-4 h-4 text-slate-500" />
              <span>Security Settings</span>
            </Link>

            <Link
              to="/settings"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <Settings className="w-4 h-4 text-slate-500" />
              <span>Workspace Preferences</span>
            </Link>
          </div>

          <div className="p-1 border-t border-slate-900 mt-1">
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2.5 px-3 py-2 text-xs font-medium text-rose-400 hover:text-rose-300 rounded-lg hover:bg-rose-500/5 transition-colors"
            >
              <LogOut className="w-4 h-4 text-rose-500/60" />
              <span>Log out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
