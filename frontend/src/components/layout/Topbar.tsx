import React from "react";
import { useTheme } from "../../context/ThemeContext";
import { Sun, Moon, Search, Bell, Shield } from "lucide-react";
import { useLocation } from "react-router-dom";
import { UserMenu } from "../auth/UserMenu";

export const Topbar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const getPageTitle = () => {
    switch (location.pathname) {
      case "/":
        return "Dashboard";
      case "/documents":
        return "Documents Workspace";
      case "/workflows":
        return "Automation Workflows";
      case "/graph":
        return "Knowledge Graph";
      case "/analytics":
        return "Platform Analytics";
      case "/settings":
        return "System Settings";
      case "/profile":
        return "Profile Settings";
      case "/security":
        return "Security Settings";
      default:
        return "Workspace";
    }
  };

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm px-6 flex items-center justify-between sticky top-0 z-10">
      {/* Page Title */}
      <div>
        <h1 className="font-semibold text-lg text-foreground">{getPageTitle()}</h1>
      </div>

      {/* Global Search Bar */}
      <div className="hidden md:flex items-center w-96 relative">
        <Search className="w-4 h-4 text-muted-foreground absolute left-3" />
        <input
          type="text"
          placeholder="Search documents, entities, workflows..."
          className="w-full bg-muted/50 border border-border rounded-lg pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:bg-background transition-all"
        />
      </div>

      {/* Topbar Actions */}
      <div className="flex items-center gap-4">
        {/* Theme Toggle Switcher */}
        <button
          onClick={toggleTheme}
          className="w-10 h-10 rounded-lg border border-border flex items-center justify-center hover:bg-muted text-muted-foreground hover:text-foreground transition-all relative overflow-hidden group"
          aria-label="Toggle Theme"
        >
          {theme === "light" ? (
            <Moon className="w-5 h-5 transition-transform duration-350 group-hover:scale-110" />
          ) : (
            <Sun className="w-5 h-5 transition-transform duration-350 group-hover:rotate-45" />
          )}
        </button>

        {/* System Notifications */}
        <button className="w-10 h-10 rounded-lg border border-border flex items-center justify-center hover:bg-muted text-muted-foreground hover:text-foreground transition-all relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary" />
        </button>

        {/* User Info & Dynamic dropdown */}
        <div className="flex items-center gap-2.5 pl-2.5 border-l border-border">
          <UserMenu />
        </div>
      </div>
    </header>
  );
};
