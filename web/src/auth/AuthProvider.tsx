import type { Session } from "@supabase/supabase-js";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { setTokenGetter } from "../api/client";
import { config } from "../config";
import { supabase } from "../lib/supabase";

export type Role = "admin" | "customer";

export interface AuthUser {
  id: string;
  email: string;
  role: Role;
}

interface AuthState {
  user: AuthUser | null;
  loading: boolean;
  /** true when the admin portal may be opened by this user */
  canUseAdmin: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<{ needsConfirmation: boolean }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

// Same rule as backend/auth.py: the app role lives in app_metadata,
// which users cannot edit themselves.
export function roleFromSession(session: Session | null): Role {
  const role = (session?.user?.app_metadata as { role?: unknown } | undefined)?.role;
  return role === "admin" ? "admin" : "customer";
}

function toUser(session: Session | null): AuthUser | null {
  if (!session?.user) return null;
  return { id: session.user.id, email: session.user.email ?? "", role: roleFromSession(session) };
}

const MOCK_USER: AuthUser = { id: "mock-admin", email: "admin@sample.local", role: "admin" };
const MOCK_SESSION_KEY = "insightdesk.mockUser";

// Mock mode keeps its fake session in sessionStorage so sign-out survives a reload.
function loadMockUser(): AuthUser | null {
  try {
    const raw = sessionStorage.getItem(MOCK_SESSION_KEY);
    if (raw === null) return MOCK_USER;
    return raw === "signed-out" ? null : (JSON.parse(raw) as AuthUser);
  } catch {
    return MOCK_USER;
  }
}

function saveMockUser(user: AuthUser | null) {
  try {
    sessionStorage.setItem(MOCK_SESSION_KEY, user ? JSON.stringify(user) : "signed-out");
  } catch {
    /* storage unavailable: the fake session just resets on reload */
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(config.authMode === "mock" ? loadMockUser : null);
  const [loading, setLoading] = useState(config.authMode !== "mock" && supabase !== null);

  useEffect(() => {
    if (!supabase) {
      setTokenGetter(async () => null);
      return;
    }
    const client = supabase;
    setTokenGetter(async () => (await client.auth.getSession()).data.session?.access_token ?? null);

    let active = true;
    client.auth.getSession().then(({ data }) => {
      if (!active) return;
      setUser(toUser(data.session));
      setLoading(false);
    });
    const { data: sub } = client.auth.onAuthStateChange((_event, session) => {
      setUser(toUser(session));
      setLoading(false);
    });
    return () => {
      active = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    if (config.authMode === "mock") {
      const u = { ...MOCK_USER, email: email || MOCK_USER.email };
      saveMockUser(u);
      setUser(u);
      return;
    }
    if (!supabase) throw new Error("Sign-in is not configured (set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY).");
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw new Error(error.message);
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    if (config.authMode === "mock") {
      const u: AuthUser = { id: "mock-customer", email, role: "customer" };
      saveMockUser(u);
      setUser(u);
      return { needsConfirmation: false };
    }
    if (!supabase) throw new Error("Sign-up is not configured (set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY).");
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw new Error(error.message);
    return { needsConfirmation: !data.session };
  }, []);

  const signOut = useCallback(async () => {
    if (supabase) await supabase.auth.signOut();
    if (config.authMode === "mock") saveMockUser(null);
    setUser(null);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      user,
      loading,
      canUseAdmin: Boolean(user) && (!config.requireAdminRole || user?.role === "admin"),
      signIn,
      signUp,
      signOut,
    }),
    [user, loading, signIn, signUp, signOut],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
