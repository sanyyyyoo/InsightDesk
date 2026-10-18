// Runtime configuration from Vite env (see .env.example).

const env = import.meta.env;

function flag(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined || value === "") return fallback;
  return ["1", "true", "yes", "on"].includes(value.trim().toLowerCase());
}

/**
 * mock   – everything from built-in sample data (no backend, no Supabase)
 * hybrid – confirmed READ-ONLY features are live; anything that writes
 *          (complaint submission, RCA generation, escalation email) and
 *          not-yet-confirmed features stay on sample data
 * live   – everything live
 */
export type DataMode = "mock" | "hybrid" | "live";

function dataMode(): DataMode {
  const v = (env.VITE_DATA_MODE || "").trim().toLowerCase();
  if (v === "mock" || v === "hybrid" || v === "live") return v;
  return flag(env.VITE_USE_MOCKS, false) ? "mock" : "live";
}

const mode = dataMode();
const authModeRaw = (env.VITE_AUTH_MODE || "").trim().toLowerCase();

export const config = {
  dataMode: mode,
  /** "mock" = fake admin session (no Supabase accounts touched); "supabase" = real sign-in */
  authMode: (authModeRaw === "mock" || authModeRaw === "supabase" ? authModeRaw : mode === "mock" ? "mock" : "supabase") as
    | "mock"
    | "supabase",
  /** Write actions hit the real backend only in live mode or when explicitly enabled. */
  writesEnabled: mode === "live" || (mode === "hybrid" && flag(env.VITE_ENABLE_WRITES, false)),
  apiUrl: (env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, ""),
  supabaseUrl: env.VITE_SUPABASE_URL || "",
  supabaseAnonKey: env.VITE_SUPABASE_ANON_KEY || "",
  requireAdminRole: flag(env.VITE_REQUIRE_ADMIN_ROLE, true),
  requestTimeoutMs: 30_000,
  // the complaint pipeline loads ML models on a cold start
  submitTimeoutMs: 120_000,
};

export const supabaseConfigured = Boolean(config.supabaseUrl && config.supabaseAnonKey);

export type Feature = "reads" | "submit" | "escalate" | "generateRca" | "reviewQueue";

/** true when a feature is served from sample data in the current mode. */
export function isSample(feature: Feature): boolean {
  if (config.dataMode === "mock") return true;
  if (feature === "reviewQueue") return true; // v2 pipeline: not built in the backend yet
  if (feature === "reads") return false;
  return !config.writesEnabled;
}
