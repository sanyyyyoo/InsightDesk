// React Query hooks: caching, de-duplicated requests, limited retries.

import { useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError } from "./client";
import { api } from "./endpoints";
import type { ComplaintSubmit } from "./types";

export const keys = {
  overview: ["overview"] as const,
  cases: ["cases"] as const,
  caseTexts: ["caseTexts"] as const,
  caseIntelligence: (id: number) => ["case", id] as const,
  clusters: ["clusters"] as const,
  topics: ["topics"] as const,
  spikes: ["spikes"] as const,
  benchmarks: ["benchmarks"] as const,
};

/** Retry only network / timeout / 5xx errors, at most twice. */
export function shouldRetry(failureCount: number, error: unknown): boolean {
  if (error instanceof ApiError && !error.isRetryable) return false;
  return failureCount < 2;
}

const STALE = 60_000;

export const useOverview = () => useQuery({ queryKey: keys.overview, queryFn: api.overview, staleTime: STALE });
export const useCases = () => useQuery({ queryKey: keys.cases, queryFn: api.cases, staleTime: STALE });
const useCaseTexts = () => useQuery({ queryKey: keys.caseTexts, queryFn: api.caseTexts, staleTime: 5 * STALE });

/**
 * Readable case title: the original wording of the case's first complaint.
 * cases.representative_text is the cleaned text (stop-words removed), so it is
 * only the fallback while the texts load or if the request fails.
 */
export function useCaseTitle() {
  const texts = useCaseTexts().data;
  return useCallback(
    (c: { case_id: number; representative_text?: string | null }) =>
      texts?.[String(c.case_id)] || c.representative_text || "–",
    [texts],
  );
}

export const useTopics = () => useQuery({ queryKey: keys.topics, queryFn: api.topics, staleTime: 5 * STALE });
export const useClusters = () => useQuery({ queryKey: keys.clusters, queryFn: api.clusters, staleTime: STALE });
export const useSpikes = () => useQuery({ queryKey: keys.spikes, queryFn: api.spikes, staleTime: STALE });
export const useBenchmarks = () => useQuery({ queryKey: keys.benchmarks, queryFn: api.benchmarks, staleTime: 5 * STALE });

export function useCaseIntelligence(caseId: number | null) {
  return useQuery({
    queryKey: keys.caseIntelligence(caseId ?? -1),
    queryFn: () => api.caseIntelligence(caseId as number),
    enabled: caseId !== null && Number.isInteger(caseId) && caseId > 0,
    staleTime: STALE,
  });
}

export function useEscalate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (caseId: number) => api.escalate(caseId),
    onSuccess: (_data, caseId) => {
      qc.invalidateQueries({ queryKey: keys.caseIntelligence(caseId) });
    },
  });
}

export function useGenerateRca() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ caseId, force }: { caseId: number; force: boolean }) => api.generateRca(caseId, force),
    onSuccess: (_data, { caseId }) => {
      qc.invalidateQueries({ queryKey: keys.caseIntelligence(caseId) });
    },
  });
}

export const useReviewQueue = () => useQuery({ queryKey: ["reviewQueue"], queryFn: api.reviewQueue, staleTime: STALE });

export function useSubmitComplaint() {
  return useMutation({ mutationFn: (body: ComplaintSubmit) => api.submitComplaint(body) });
}

export function useChat() {
  return useMutation({ mutationFn: (message: string) => api.chat(message) });
}
