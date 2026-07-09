import { create } from "zustand";

export interface Citation {
  id: string;
  asset_id: string;
  asset_name: string;
  snippet: string;
  confidence_score: number;
}

export interface Message {
  role: "system" | "user" | "assistant";
  content: string;
  citations?: Citation[];
  timestamp: string;
}

interface ChatState {
  messages: Message[];
  citations: Citation[];
  loading: boolean;
  preferredProvider: string;
  activeProjectId: string | null;
  activeCollectionId: string | null;
  setPreferredProvider: (provider: string) => void;
  setProjectFilter: (projectId: string | null) => void;
  setCollectionFilter: (collectionId: string | null) => void;
  clearChat: () => void;
  sendMessage: (query: string, workspaceId: string, token: string | null) => Promise<void>;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  citations: [],
  loading: false,
  preferredProvider: "ollama",
  activeProjectId: null,
  activeCollectionId: null,

  setPreferredProvider: (provider) => set({ preferredProvider: provider }),
  setProjectFilter: (projectId) => set({ activeProjectId: projectId }),
  setCollectionFilter: (collectionId) => set({ activeCollectionId: collectionId }),
  clearChat: () => set({ messages: [], citations: [] }),

  sendMessage: async (query, workspaceId, token) => {
    if (!query.trim()) return;

    const userMessage: Message = {
      role: "user",
      content: query,
      timestamp: new Date().toISOString(),
    };

    const initialAssistantMessage: Message = {
      role: "assistant",
      content: "",
      citations: [],
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, userMessage, initialAssistantMessage],
      loading: true,
      citations: [],
    }));

    try {
      const historyPayload = get().messages
        .slice(0, -2) // Exclude current query and mock assistant message
        .map((msg) => ({ role: msg.role, content: msg.content }));

      const response = await fetch("http://localhost:8000/api/v1/knowledge/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token || ""}`,
        },
        body: JSON.stringify({
          query,
          workspace_id: workspaceId,
          project_id: get().activeProjectId,
          collection_id: get().activeCollectionId,
          history: historyPayload,
          preferred_provider: get().preferredProvider,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to initialize conversation stream.");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) return;

      let assistantText = "";
      let activeCitations: Citation[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              
              if (data.status === "started" && data.citations) {
                activeCitations = data.citations;
                set({ citations: activeCitations });
              } else if (data.status === "streaming" && data.text) {
                assistantText += data.text;
                
                // Update active assistant message text
                set((state) => {
                  const updated = [...state.messages];
                  const lastIdx = updated.length - 1;
                  updated[lastIdx] = {
                    ...updated[lastIdx],
                    content: assistantText,
                    citations: activeCitations,
                  };
                  return { messages: updated };
                });
              }
            } catch (e) {
              // Ignore partial parse lines
            }
          }
        }
      }
    } catch (error: any) {
      console.error(error);
      set((state) => {
        const updated = [...state.messages];
        const lastIdx = updated.length - 1;
        updated[lastIdx] = {
          ...updated[lastIdx],
          content: `Error: ${error.message || "Failed to retrieve answer."}`,
        };
        return { messages: updated };
      });
    } finally {
      set({ loading: false });
    }
  },
}));
