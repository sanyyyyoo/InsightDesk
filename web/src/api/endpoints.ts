// One function per backend endpoint. Each feature is served live or from
// sample data according to config.dataMode (see isSample in config.ts).

import { config, isSample } from "../config";
import { mockApi } from "../mocks/mockApi";
import { apiRequest } from "./client";
import type {
  Benchmark,
  Case,
  CaseIntelligence,
  CaseTexts,
  ChatResponse,
  Clusters,
  ComplaintSubmit,
  EscalateResponse,
  GroupSpike,
  Overview,
  Rca,
  SpikeCase,
  SubmitResult,
  UnassignedSpikes,
  Topic,
} from "./types";

const real = {
  overview: () => apiRequest<Overview>("/dashboard/overview"),
  cases: () => apiRequest<Case[]>("/dashboard/cases"),
  caseTexts: () => apiRequest<CaseTexts>("/dashboard/case-texts"),
  caseIntelligence: (caseId: number) => apiRequest<CaseIntelligence>(`/dashboard/cases/${caseId}/intelligence`),
  clusters: () => apiRequest<Clusters>("/dashboard/clusters"),
  topics: () => apiRequest<Topic[]>("/dashboard/topics"),
  spikes: () => apiRequest<SpikeCase[]>("/dashboard/spikes", { timeoutMs: 60_000 }),
  groupSpikes: () => apiRequest<GroupSpike[]>("/dashboard/group-spikes", { timeoutMs: 60_000 }),
  unassignedSpikes: () => apiRequest<UnassignedSpikes>("/dashboard/unassigned-spikes", { timeoutMs: 60_000 }),
  benchmarks: () => apiRequest<Benchmark[]>("/dashboard/benchmarks"),
  chat: (message: string) => apiRequest<ChatResponse>("/chat", { method: "POST", body: { message }, timeoutMs: 90_000 }),
  // ---- writes ----
  escalate: (caseId: number) => apiRequest<EscalateResponse>(`/dashboard/cases/${caseId}/escalate`, { method: "POST" }),
  generateRca: (caseId: number, force: boolean) =>
    apiRequest<Rca>(`/dashboard/cases/${caseId}/rca${force ? "?force=true" : ""}`, { method: "POST", timeoutMs: 120_000 }),
  submitComplaint: (body: ComplaintSubmit) =>
    apiRequest<SubmitResult>("/analyze", { method: "POST", body, timeoutMs: config.submitTimeoutMs }),
};

export type Api = typeof real;

const pick = <K extends keyof Api>(key: K, sample: boolean): Api[K] => (sample ? mockApi[key] : real[key]) as Api[K];
const reads = isSample("reads");

export const api: Api = {
  overview: pick("overview", reads),
  cases: pick("cases", reads),
  caseTexts: pick("caseTexts", reads),
  caseIntelligence: pick("caseIntelligence", reads),
  clusters: pick("clusters", reads),
  topics: pick("topics", reads),
  spikes: pick("spikes", reads),
  groupSpikes: pick("groupSpikes", reads),
  unassignedSpikes: pick("unassignedSpikes", reads),
  benchmarks: pick("benchmarks", reads),
  chat: pick("chat", reads),
  escalate: pick("escalate", isSample("escalate")),
  generateRca: pick("generateRca", isSample("generateRca")),
  submitComplaint: pick("submitComplaint", isSample("submit")),
};
