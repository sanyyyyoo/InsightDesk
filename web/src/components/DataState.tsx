import type { UseQueryResult } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { ApiError, friendlyMessage } from "../api/client";

export function Loading({ label = "Loading…", fullPage = false }: { label?: string; fullPage?: boolean }) {
  const body = (
    <div className="state row" role="status" aria-live="polite" style={{ justifyContent: "center" }}>
      <span className="spinner" aria-hidden /> <span>{label}</span>
    </div>
  );
  return fullPage ? <div className="center-page" style={{ background: "var(--bg)" }}>{body}</div> : body;
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const retryable = !(error instanceof ApiError) || error.isRetryable;
  return (
    <div className="alert alert-error row between" role="alert">
      <span>{friendlyMessage(error)}</span>
      {onRetry && retryable && (
        <button className="btn btn-secondary" onClick={onRetry} type="button">
          Retry
        </button>
      )}
    </div>
  );
}

export function Empty({ children }: { children: ReactNode }) {
  return <div className="state">{children}</div>;
}

/** Renders loading / error / empty states for a query, then the content. */
export function QueryState<T>({
  query,
  isEmpty,
  empty,
  loadingLabel,
  children,
}: {
  query: UseQueryResult<T>;
  isEmpty?: (data: T) => boolean;
  empty?: ReactNode;
  loadingLabel?: string;
  children: (data: T) => ReactNode;
}) {
  if (query.isPending) return <Loading label={loadingLabel} />;
  if (query.isError) return <ErrorState error={query.error} onRetry={() => query.refetch()} />;
  if (isEmpty && isEmpty(query.data)) return <Empty>{empty ?? "Nothing to show yet."}</Empty>;
  return <>{children(query.data)}</>;
}
