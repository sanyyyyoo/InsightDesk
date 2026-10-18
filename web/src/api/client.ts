// Small fetch wrapper: base URL, bearer token, timeout, and errors that
// carry the HTTP status plus the backend's "detail" message.

import { config } from "../config";

export class ApiError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }

  get isAuth(): boolean {
    return this.status === 401;
  }

  get isForbidden(): boolean {
    return this.status === 403;
  }

  /** Network failure, timeout or server error: worth a retry. */
  get isRetryable(): boolean {
    return this.status === 0 || this.status === 408 || this.status >= 500;
  }
}

type TokenGetter = () => Promise<string | null>;
let getToken: TokenGetter = async () => null;

/** Registered by the auth provider so every request carries the session token. */
export function setTokenGetter(fn: TokenGetter): void {
  getToken = fn;
}

export function friendlyMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 0) return "Cannot reach the InsightDesk API. Is the backend running?";
    if (error.status === 408) return "The request timed out. Please try again.";
    if (error.isAuth) return "Your session has expired. Please sign in again.";
    if (error.isForbidden) return "This needs an admin account.";
    if (error.status === 404) return error.detail || "Not found.";
    return error.detail || `Request failed (${error.status}).`;
  }
  if (error instanceof Error) return error.message;
  return "Something went wrong.";
}

function extractDetail(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    // FastAPI validation errors: [{loc, msg, type}, ...]
    if (Array.isArray(detail)) {
      return detail
        .map((d) => (d && typeof d === "object" && "msg" in d ? String((d as { msg: unknown }).msg) : String(d)))
        .join("; ");
    }
  }
  return fallback;
}

export interface RequestOptions {
  method?: "GET" | "POST";
  body?: unknown;
  timeoutMs?: number;
  signal?: AbortSignal;
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, timeoutMs = config.requestTimeoutMs, signal } = options;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort("timeout"), timeoutMs);
  const onAbort = () => controller.abort("cancelled");
  signal?.addEventListener("abort", onAbort);

  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = await getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${config.apiUrl}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: controller.signal,
    });
  } catch {
    if (controller.signal.aborted && controller.signal.reason === "timeout") {
      throw new ApiError(408, "Request timed out.");
    }
    if (signal?.aborted) throw new ApiError(499, "Request cancelled.");
    throw new ApiError(0, "Network error.");
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener("abort", onAbort);
  }

  let payload: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, extractDetail(payload, response.statusText || "Request failed"));
  }
  return payload as T;
}
