import { createBrowserRouter } from "react-router-dom";
import { Layout } from "../components/layout/Layout";
import { Dashboard } from "../pages/Dashboard";
import { Chat } from "../pages/Chat";
import { Research } from "../pages/Research";
import { LegalStudio } from "../pages/LegalStudio";
import { Documents } from "../pages/Documents";
import { Workflows } from "../pages/Workflows";
import { KnowledgeGraph } from "../pages/KnowledgeGraph";
import { Analytics } from "../pages/Analytics";
import { Settings } from "../pages/Settings";
import { Login } from "../pages/Login";
import { Register } from "../pages/Register";
import { Profile } from "../pages/Profile";
import { Security } from "../pages/Security";
import { ProtectedRoute } from "../components/auth/ProtectedRoute";

export const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Dashboard /> },
      { path: "chat", element: <Chat /> },
      { path: "research", element: <Research /> },
      { path: "legal", element: <LegalStudio /> },
      { path: "documents", element: <Documents /> },
      { path: "workflows", element: <Workflows /> },
      { path: "graph", element: <KnowledgeGraph /> },
      { path: "analytics", element: <Analytics /> },
      { path: "settings", element: <Settings /> },
      { path: "profile", element: <Profile /> },
      { path: "security", element: <Security /> },
    ],
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/register",
    element: <Register />,
  },
]);
