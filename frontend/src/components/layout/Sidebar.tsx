import React from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  LayoutDashboard, 
  Files, 
  Workflow, 
  Network, 
  BarChart3, 
  Settings, 
  ChevronLeft, 
  ChevronRight,
  Cpu,
  BookOpen,
  Scale
} from "lucide-react";
import { cn } from "../../utils/cn";
import { WorkspaceSwitcher } from "../workspaces/WorkspaceSwitcher";

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed }) => {
  const location = useLocation();

  const menuItems = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Legal Studio", path: "/legal", icon: Scale },
    { name: "Research Studio", path: "/research", icon: BookOpen },
    { name: "AI Chat", path: "/chat", icon: Cpu },
    { name: "Documents", path: "/documents", icon: Files },
    { name: "Workflows", path: "/workflows", icon: Workflow },
    { name: "Knowledge Graph", path: "/graph", icon: Network },
    { name: "Analytics", path: "/analytics", icon: BarChart3 },
    { name: "Settings", path: "/settings", icon: Settings },
  ];

  return (
    <aside 
      className={cn(
        "h-screen bg-card border-r border-border flex flex-col transition-all duration-300 relative z-20",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Dynamic Workspace Switcher Header */}
      <div className="h-16 flex items-center px-3 border-b border-border gap-2 overflow-hidden shrink-0">
        <WorkspaceSwitcher collapsed={collapsed} />
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group relative",
                isActive 
                  ? "bg-primary text-primary-foreground shadow-sm" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span className="transition-opacity duration-200">{item.name}</span>}
              
              {/* Tooltip for collapsed mode */}
              {collapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-foreground text-background text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none whitespace-nowrap z-50">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="h-10 border-t border-border flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
      >
        {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronLeft className="w-5 h-5" />}
      </button>
    </aside>
  );
};
