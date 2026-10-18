import { useState, type FormEvent } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";
import { Loading } from "../components/DataState";
import { config, supabaseConfigured } from "../config";

export function LoginPage() {
  const { user, loading, canUseAdmin, signIn, signUp } = useAuth();
  const location = useLocation();
  const [mode, setMode] = useState<"in" | "up">("in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  if (loading) return <Loading label="Checking your session…" fullPage />;
  if (user) {
    const from = (location.state as { from?: string } | null)?.from;
    const target = from && (!from.startsWith("/admin") || canUseAdmin) ? from : canUseAdmin ? "/admin" : "/submit";
    return <Navigate to={target} replace />;
  }

  const notConfigured = config.authMode !== "mock" && !supabaseConfigured;
  const emailOk = /^\S+@\S+\.\S+$/.test(email);
  const passwordOk = password.length >= 8;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setInfo(null);
    if (!emailOk) return setError("Enter a valid email address.");
    if (!passwordOk) return setError("Password must be at least 8 characters.");
    setBusy(true);
    try {
      if (mode === "in") {
        await signIn(email.trim(), password);
      } else {
        const { needsConfirmation } = await signUp(email.trim(), password);
        if (needsConfirmation) setInfo("Account created. Check your email to confirm it, then sign in.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="center-page">
      <form className="card auth-card stack" onSubmit={onSubmit} noValidate>
        <div>
          <h2>InsightDesk</h2>
          <p className="muted small">Sign in to report a problem, or as an operator to open the dashboard.</p>
        </div>
        {config.authMode === "mock" && <div className="alert alert-info small">Sample mode: any email and an 8+ character password works.</div>}
        {notConfigured && (
          <div className="alert alert-warning small">
            Sign-in is not configured. Set <code>VITE_SUPABASE_URL</code> and <code>VITE_SUPABASE_ANON_KEY</code> in{" "}
            <code>web/.env.local</code>.
          </div>
        )}
        <div className="tabs" role="tablist">
          <button type="button" role="tab" aria-selected={mode === "in"} className={mode === "in" ? "active" : ""} onClick={() => setMode("in")}>
            Sign in
          </button>
          <button type="button" role="tab" aria-selected={mode === "up"} className={mode === "up" ? "active" : ""} onClick={() => setMode("up")}>
            Create account
          </button>
        </div>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" className="input" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            className="input"
            type="password"
            autoComplete={mode === "in" ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {mode === "up" && <span className="hint">At least 8 characters.</span>}
        </div>
        {error && <div className="alert alert-error small" role="alert">{error}</div>}
        {info && <div className="alert alert-success small">{info}</div>}
        <button className="btn" type="submit" disabled={busy || notConfigured}>
          {busy && <span className="spinner" aria-hidden />}
          {mode === "in" ? "Sign in" : "Create account"}
        </button>
      </form>
    </div>
  );
}
