import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  X, 
  Minus, 
  Maximize2, 
  Send, 
  Terminal, 
  Search, 
  Sparkles, 
  Command, 
  Copy,
  Check
} from "lucide-react";
import { cn } from "../../utils/cn";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store/auth";

interface Message {
  id: string;
  sender: "user" | "nyra";
  text: string;
  isStreaming?: boolean;
}

export const NyraAssistant: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "nyra",
      text: "System initialized. I am Nyra, your Enterprise Intelligence Operating Assistant. I can index documents, build knowledge graphs, construct automation workflows, and navigate this environment. What would you like to build or inspect today?"
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { accessToken, logout } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    
    const queryToSend = input;
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch("http://localhost:8000/api/v1/assistant/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": accessToken ? `Bearer ${accessToken}` : "",
        },
        body: JSON.stringify({ query: queryToSend }),
      });

      setIsTyping(false);

      if (!response.ok) {
        throw new Error("Failed to communicate with Nyra backend assistant.");
      }

      const data = await response.json();
      const nyraMsgId = Date.now().toString();

      // Append Nyra's response to message list
      setMessages((prev) => [...prev, { id: nyraMsgId, sender: "nyra", text: data.text }]);

      // Check for navigation command
      if (data.navigate_to) {
        setTimeout(() => {
          navigate(data.navigate_to);
        }, 800);
      }

      // Check for execute commands
      if (data.execute_command === "logout") {
        setTimeout(async () => {
          await logout();
          navigate("/login");
        }, 1000);
      }

    } catch (err: any) {
      setIsTyping(false);
      const errId = Date.now().toString();
      setMessages((prev) => [
        ...prev,
        { id: errId, sender: "nyra", text: `Error: ${err.message || "Failed to contact Nyra service."}` }
      ]);
    }
  };

  const handleQuickAction = (text: string) => {
    setInput(text);
  };

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Floating Chat Window */}
      <AnimatePresence>
        {isOpen && !isMinimized && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            transition={{ type: "spring", damping: 25, stiffness: 250 }}
            className={cn(
              "bg-card/95 border border-border shadow-2xl rounded-xl flex flex-col overflow-hidden mb-4 backdrop-blur-md transition-all duration-300",
              isExpanded ? "w-[700px] h-[650px]" : "w-[400px] h-[500px]"
            )}
          >
            {/* Window Header */}
            <div className="h-12 border-b border-border bg-muted/30 px-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                {/* Geometric Logo */}
                <div className="w-5 h-5 rounded bg-primary flex items-center justify-center text-primary-foreground">
                  <svg viewBox="0 0 24 24" className="w-3.5 h-3.5" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <span className="font-semibold text-sm text-foreground">Nyra OS Assistant</span>
                <span className="text-[10px] bg-primary/10 text-primary px-1.5 py-0.5 rounded font-mono">v1.0</span>
              </div>
              <div className="flex items-center gap-1.5">
                <button 
                  onClick={() => setIsMinimized(true)}
                  className="p-1 hover:bg-muted text-muted-foreground hover:text-foreground rounded transition-colors"
                >
                  <Minus className="w-3.5 h-3.5" />
                </button>
                <button 
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="p-1 hover:bg-muted text-muted-foreground hover:text-foreground rounded transition-colors"
                >
                  <Maximize2 className="w-3.5 h-3.5" />
                </button>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-muted text-muted-foreground hover:text-foreground rounded transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg) => (
                <div 
                  key={msg.id} 
                  className={cn(
                    "flex flex-col max-w-[85%] rounded-lg p-3 text-sm transition-all",
                    msg.sender === "user" 
                      ? "bg-primary text-primary-foreground ml-auto" 
                      : "bg-muted text-foreground mr-auto border border-border"
                  )}
                >
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {msg.text}
                  </div>
                  {msg.sender === "nyra" && msg.text.includes("ollama") && (
                    <button 
                      onClick={() => copyToClipboard(msg.text, msg.id)}
                      className="mt-2 self-end text-[10px] flex items-center gap-1 opacity-60 hover:opacity-100 transition-opacity"
                    >
                      {copiedId === msg.id ? (
                        <>
                          <Check className="w-3 h-3 text-green-500" /> Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" /> Copy
                        </>
                      )}
                    </button>
                  )}
                </div>
              ))}
              {isTyping && (
                <div className="bg-muted text-foreground border border-border mr-auto rounded-lg p-3 text-sm max-w-[85%] flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions Panel */}
            <div className="px-4 py-2 bg-muted/10 border-t border-border flex flex-wrap gap-1.5">
              <button 
                onClick={() => handleQuickAction("Analyze system diagnostics")}
                className="text-[11px] px-2 py-1 bg-muted hover:bg-primary/10 hover:text-primary rounded-md border border-border transition-colors flex items-center gap-1"
              >
                <Terminal className="w-3.5 h-3.5" /> Diagnose OS
              </button>
              <button 
                onClick={() => handleQuickAction("Search database structure")}
                className="text-[11px] px-2 py-1 bg-muted hover:bg-primary/10 hover:text-primary rounded-md border border-border transition-colors flex items-center gap-1"
              >
                <Search className="w-3.5 h-3.5" /> Search DB
              </button>
              <button 
                onClick={() => handleQuickAction("Explain interface layout")}
                className="text-[11px] px-2 py-1 bg-muted hover:bg-primary/10 hover:text-primary rounded-md border border-border transition-colors flex items-center gap-1"
              >
                <Sparkles className="w-3.5 h-3.5" /> Explain UI
              </button>
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSend} className="p-3 border-t border-border bg-muted/20 flex gap-2">
              <div className="flex-1 relative flex items-center">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Nyra to execute commands or guide..."
                  className="w-full bg-background border border-border rounded-lg pl-3 pr-10 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary"
                />
                <kbd className="hidden md:flex items-center gap-0.5 absolute right-2.5 px-1.5 py-0.5 bg-muted border border-border rounded text-[10px] text-muted-foreground font-mono">
                  <Command className="w-2.5 h-2.5" /> K
                </kbd>
              </div>
              <button 
                type="submit"
                className="w-10 h-10 bg-primary text-primary-foreground hover:bg-primary/95 rounded-lg flex items-center justify-center transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Toggle Bubble */}
      <div className="flex items-center gap-2">
        {/* Minimized HUD indicator */}
        {isOpen && isMinimized && (
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={() => setIsMinimized(false)}
            className="px-3 py-1.5 bg-card border border-border hover:border-primary shadow-lg rounded-lg text-xs cursor-pointer flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-all"
          >
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            Nyra Minimized
          </motion.div>
        )}
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => {
            if (isMinimized) {
              setIsMinimized(false);
            } else {
              setIsOpen(!isOpen);
            }
          }}
          className={cn(
            "w-12 h-12 rounded-full shadow-2xl flex items-center justify-center text-primary-foreground transition-all duration-300 relative",
            isOpen && !isMinimized 
              ? "bg-muted text-foreground border border-border" 
              : "bg-primary text-primary-foreground hover:bg-primary/90"
          )}
          aria-label="Nyra Intelligence Assistant"
        >
          {isOpen && !isMinimized ? (
            <X className="w-5 h-5" />
          ) : (
            <div className="flex items-center justify-center">
              <svg viewBox="0 0 24 24" className="w-6 h-6 animate-pulse" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
          )}
        </motion.button>
      </div>
    </div>
  );
};
