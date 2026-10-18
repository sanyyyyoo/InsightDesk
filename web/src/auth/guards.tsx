import type { ReactNode } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import { Loading } from "../components/DataState";
import { useAuth } from "./AuthProvider";

export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Loading label="Checking your session…" fullPage />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}

export function RequireAdmin({ children }: { children: ReactNode }) {
  const { user, loading, canUseAdmin } = useAuth();
  const location = useLocation();
  if (loading) return <Loading label="Checking your session…" fullPage />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (!canUseAdmin) {
    return (
      <div className="center-page">
        <div className="card auth-card stack">
          <h2>Admin access required</h2>
          <p className="muted">
            You are signed in as <b>{user.email}</b>, which is a customer account. Operators need an account whose
            Supabase <code>app_metadata.role</code> is <code>admin</code>.
          </p>
          <Link className="btn" to="/submit">
            Go to the complaint portal
          </Link>
        </div>
      </div>
    );
  }
  return <>{children}</>;
}
