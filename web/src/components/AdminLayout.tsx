import { NavLink, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { config } from "../config";
import { ErrorBoundary } from "./ErrorBoundary";

const NAV = [
  { to: "/admin", label: "Overview", end: true },
  { to: "/admin/cases", label: "Cases" },
  { to: "/admin/incidents", label: "Incident Response" },
  { to: "/admin/sentiment", label: "Sentiment" },
  { to: "/admin/topics", label: "Topics" },
  { to: "/admin/assistant", label: "AI Assistant" },
];

export function AdminLayout() {
  const { user, signOut } = useAuth();
  const location = useLocation();
  return (
    <>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">InsightDesk</div>
          <div className="brand-sub">AI Complaint Intelligence</div>
          <nav aria-label="Admin">
            {NAV.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => (isActive ? "active" : undefined)}>
                {n.label}
              </NavLink>
            ))}
          </nav>
          <div className="spacer" />
          <div className="user-box">
            <div>{user?.email}</div>
            <div>Role: {user?.role}</div>
            <button className="btn btn-ghost" type="button" onClick={() => signOut()}>
              Sign out
            </button>
          </div>
        </aside>
        <main className="main">
          {config.dataMode === "mock" && <div className="dev-banner">Sample data mode – nothing is read from or written to the real backend.</div>}
          {config.dataMode === "hybrid" && (
            <div className="dev-banner">
              Hybrid mode – dashboards read live data; {config.writesEnabled ? "write actions are LIVE" : "RCA generation, escalation and complaint submission are simulated (nothing is written)"}
              {config.authMode === "mock" && " Sign-in is simulated."}
            </div>
          )}
          {config.dataMode !== "mock" && config.authMode === "supabase" && !config.requireAdminRole && (
            <div className="dev-banner">Dev mode: admin role is not enforced in the browser (VITE_REQUIRE_ADMIN_ROLE=false).</div>
          )}
          <ErrorBoundary resetKey={location.pathname}>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
    </>
  );
}
