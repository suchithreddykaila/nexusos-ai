import React, { useState, useRef, useEffect } from "react";
import { useWorkspaceStore } from "../../store/workspace";
import { useAuthStore } from "../../store/auth";
import { ChevronDown, Plus, Check, Briefcase, Settings } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface WorkspaceSwitcherProps {
  collapsed: boolean;
}

export const WorkspaceSwitcher: React.FC<WorkspaceSwitcherProps> = ({ collapsed }) => {
  const { workspaces, activeWorkspace, switchWorkspace, fetchWorkspaces } = useWorkspaceStore();
  const { accessToken } = useAuthStore();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (accessToken) {
      fetchWorkspaces(accessToken);
    }
  }, [accessToken, fetchWorkspaces]);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, []);

  const handleSwitch = async (wsId: string) => {
    if (!accessToken) return;
    setOpen(false);
    await switchWorkspace(accessToken, wsId);
  };

  const handleCreateNew = () => {
    setOpen(false);
    navigate("/settings"); // Settings has the workspace create buttons mapped
  };

  if (!activeWorkspace) {
    return (
      <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center text-white font-bold text-xs shrink-0 animate-pulse">
        N
      </div>
    );
  }

  const initials = activeWorkspace.name.substring(0, 2).toUpperCase();

  return (
    <div className="relative font-sans text-slate-100 w-full" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-1.5 rounded-lg border border-slate-800/80 hover:bg-slate-900/60 hover:border-slate-700 transition-all outline-none"
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <div className="w-7 h-7 rounded-md bg-gradient-to-tr from-indigo-500 to-violet-500 text-white font-bold text-xs flex items-center justify-center shadow-md shrink-0">
            {activeWorkspace.logo_url ? (
              <img src={activeWorkspace.logo_url} alt={activeWorkspace.name} className="w-full h-full object-cover rounded-md" />
            ) : (
              initials
            )}
          </div>
          {!collapsed && (
            <span className="text-xs font-bold text-left truncate max-w-[120px]">
              {activeWorkspace.name}
            </span>
          )}
        </div>
        {!collapsed && <ChevronDown className="w-3.5 h-3.5 text-slate-500 shrink-0" />}
      </button>

      {open && !collapsed && (
        <div className="absolute left-0 mt-2 w-56 rounded-xl bg-slate-950/90 border border-slate-850 shadow-2xl backdrop-blur-xl py-1.5 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="px-4 py-2 border-b border-slate-900">
            <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Switch Workspace
            </span>
          </div>

          <div className="p-1 flex flex-col gap-0.5 max-h-48 overflow-y-auto">
            {workspaces.map((ws) => (
              <button
                key={ws.id}
                onClick={() => handleSwitch(ws.id)}
                className="w-full flex items-center justify-between px-3 py-2 text-xs font-medium text-slate-400 hover:text-slate-200 rounded-lg hover:bg-slate-900 transition-colors"
              >
                <div className="flex items-center gap-2 truncate">
                  <Briefcase className="w-3.5 h-3.5 text-slate-500" />
                  <span className="truncate">{ws.name}</span>
                </div>
                {ws.id === activeWorkspace.id && <Check className="w-3.5 h-3.5 text-indigo-400" />}
              </button>
            ))}
          </div>

          <div className="p-1 border-t border-slate-900 mt-1">
            <button
              onClick={handleCreateNew}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-indigo-400 hover:text-indigo-300 rounded-lg hover:bg-indigo-500/5 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Configure Workspaces</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
