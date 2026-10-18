// Sample data for `npm run dev:mock` and tests. Shapes match the backend
// exactly; content is illustrative (helpdesk SaaS complaints).

import type {
  Benchmark,
  Case,
  CaseIntelligence,
  CaseTexts,
  ChatResponse,
  Clusters,
  Complaint,
  ComplaintSubmit,
  EscalateResponse,
  Overview,
  Rca,
  ReviewItem,
  SpikeCase,
  SubmitResult,
  Topic,
} from "../api/types";
import { ApiError } from "../api/client";

const delay = (ms = 250) => new Promise((r) => setTimeout(r, ms));

const topics: Topic[] = [
  { topic_id: 1, topic_name: "Login & verification codes", department: "Engineering", description: "OTP / 2FA codes not arriving, SSO failures" },
  { topic_id: 2, topic_name: "Performance & loading", department: "Engineering", description: "Slow dashboards and pages" },
  { topic_id: 3, topic_name: "Billing & refunds", department: "Billing", description: "Double charges, refunds, invoices" },
  { topic_id: 4, topic_name: "Notifications", department: "Product", description: "Missing or delayed notifications" },
  { topic_id: 5, topic_name: "Support responsiveness", department: "Customer Success", description: "No reply, escalations ignored" },
];

const seeds: [string, number, string, number][] = [
  // text, topic, sentiment, reports
  ["never received the OTP when trying to log in", 1, "negative", 42],
  ["SSO login spins and never completes", 1, "negative", 17],
  ["dashboard takes over a minute to load basic data", 2, "negative", 31],
  ["charged twice for the same subscription this month", 3, "negative", 26],
  ["push notifications stopped working a week ago", 4, "negative", 19],
  ["submitted a support ticket three days ago and no reply", 5, "negative", 14],
  ["refund approved but money never came back", 3, "negative", 12],
  ["export to CSV fails every time", 2, "negative", 9],
  ["invoice PDF is missing the billing address", 3, "neutral", 6],
  ["session expires every few minutes while active", 1, "negative", 11],
  ["search returns nothing for tickets I know exist", 2, "negative", 8],
  ["live chat shows available but no one responds", 5, "negative", 7],
  ["new reporting feature works well, thanks", 2, "positive", 3],
  ["notifications arrive hours late on mobile", 4, "negative", 5],
  ["attachments fail to upload on Android", 2, "negative", 4],
  ["cannot change the email linked to my account", 1, "neutral", 3],
];

const now = Date.now();
const iso = (hoursAgo: number) => new Date(now - hoursAgo * 3600_000).toISOString();

const cases: Case[] = seeds.map(([text, topic, sentiment, reports], i) => ({
  case_id: 101 + i,
  representative_text: text,
  report_count: reports,
  user_ids: [],
  topic_id: topic,
  sentiment,
  confidence_score: 0.72 + ((i * 7) % 25) / 100,
  sentiment_model: "roberta",
  created_at: iso(24 * (10 + i)),
  last_reported_at: iso(2 + i * 3),
}));

const spikeOf = (c: Case) => {
  const z = c.report_count >= 25 ? 3.4 : c.report_count >= 15 ? 2.3 : 0.6;
  return { spike: z > 2, critical: z > 3, z_score: z, current: Math.max(1, Math.round(c.report_count / 4)) };
};

const rcas: Record<number, Rca> = {
  101: {
    case_id: 101,
    probable_cause: "SMS delivery provider is failing for some carriers, so OTP codes are not delivered.",
    affected_segment: "Users signing in with SMS-based two-factor authentication",
    recommended_action: "Check SMS gateway delivery reports; add email fallback for OTP.",
    severity: "CRITICAL",
    confidence: 0.82,
    source_evidence: ["never received the OTP when trying to log in", "OTP delivery is broken, waited 20 minutes"],
    generated_at: iso(3),
    model_used: "groq:openai/gpt-oss-120b",
  },
  103: {
    case_id: 103,
    probable_cause: "Dashboard queries slow down at peak hours.",
    affected_segment: "Agents opening the dashboard during business hours",
    recommended_action: "Profile dashboard queries and add caching for summary widgets.",
    severity: "HIGH",
    confidence: 0.71,
    source_evidence: ["dashboard takes over a minute to load basic data"],
    generated_at: iso(6),
    model_used: "groq:openai/gpt-oss-120b",
  },
};

function complaintsFor(c: Case): Complaint[] {
  const variants = [c.representative_text, `Still happening: ${c.representative_text}`, `${c.representative_text}. Please fix this soon.`];
  return Array.from({ length: Math.min(c.report_count, 8) }, (_, k) => ({
    complaint_id: c.case_id * 100 + k,
    complaint_text: variants[k % variants.length],
    user_id: `user-${(k * 13) % 50}`,
    rating: 1 + (k % 2),
    source: k % 3 === 0 ? "web_portal" : "google_play_store",
    product: "Helpdesk",
    case_id: c.case_id,
    is_duplicate: k > 0,
    created_at: iso(2 + k * 5),
  }));
}

const volume = Array.from({ length: 21 }, (_, d) => {
  const date = new Date(now - (20 - d) * 86_400_000).toISOString().slice(0, 10);
  return { date, label: `${date.slice(5, 7)}/${date.slice(8, 10)}`, count: 18 + ((d * 37) % 23) + (d > 16 ? 25 : 0) };
});

const benchmarks: Benchmark[] = [
  { model_name: "roberta", complaints_processed: 1432, average_latency_ms: 41.2, throughput: 24.3, memory_mb: 512 },
  { model_name: "distilbert", complaints_processed: 1432, average_latency_ms: 23.5, throughput: 42.6, memory_mb: 268 },
];

let escalated = new Set<number>();

export const mockApi = {
  async caseTexts(): Promise<CaseTexts> {
    await delay();
    return Object.fromEntries(cases.map((c) => [String(c.case_id), c.representative_text]));
  },
  async overview(): Promise<Overview> {
    await delay();
    const spike_cases: SpikeCase[] = cases
      .map((c) => ({ case_id: c.case_id, representative_text: c.representative_text, ...spikeOf(c) }))
      .filter((s) => s.spike);
    return {
      complaints: cases.reduce((n, c) => n + c.report_count, 0),
      cases: cases.length,
      topics: topics.length,
      spikes: spike_cases.length,
      spike_cases,
      benchmarks,
      topics_data: topics,
      volume_by_day: volume,
    };
  },
  async cases(): Promise<Case[]> {
    await delay();
    return cases;
  },
  async caseIntelligence(caseId: number): Promise<CaseIntelligence> {
    await delay();
    const c = cases.find((x) => x.case_id === caseId);
    if (!c) throw new ApiError(404, `Case ${caseId} not found.`);
    return {
      case: c,
      complaints: complaintsFor(c),
      topic: topics.find((t) => t.topic_id === c.topic_id) ?? null,
      spike: spikeOf(c),
      rca: rcas[caseId] ?? null,
    };
  },
  async clusters(): Promise<Clusters> {
    await delay();
    return {
      case_count: cases.length,
      topic_count: topics.length,
      outlier_count: 2,
      outlier_rate: 2 / cases.length,
      clustering_version: 3,
      last_clustered_at: iso(30),
      topics: topics
        .map((t) => {
          const assigned = cases.filter((c) => c.topic_id === t.topic_id);
          return {
            topic_id: t.topic_id,
            topic_name: t.topic_name,
            department: t.department,
            description: t.description,
            case_count: assigned.length,
            representative_cases: assigned.slice(0, 5).map(({ case_id, representative_text, sentiment, report_count }) => ({
              case_id,
              representative_text,
              sentiment,
              report_count,
            })),
          };
        })
        .sort((a, b) => b.case_count - a.case_count),
    };
  },
  async topics(): Promise<Topic[]> {
    await delay();
    return topics;
  },
  async spikes(): Promise<SpikeCase[]> {
    await delay();
    return cases.map((c) => ({ case_id: c.case_id, representative_text: c.representative_text, ...spikeOf(c) })).filter((s) => s.spike);
  },
  async benchmarks(): Promise<Benchmark[]> {
    await delay();
    return benchmarks;
  },
  async escalate(caseId: number): Promise<EscalateResponse> {
    await delay(500);
    escalated = new Set(escalated).add(caseId);
    return { status: "success", case_id: caseId, message: `Sample: case #${caseId} escalation simulated – no email was sent.` };
  },
  async generateRca(caseId: number, _force: boolean): Promise<Rca> {
    await delay(900);
    const c = cases.find((x) => x.case_id === caseId);
    return {
      case_id: caseId,
      probable_cause: `Sample RCA – not generated by the LLM and not saved. ${
        c ? `Reports point to a recurring failure: "${c.representative_text}".` : "Real RCAs come from the case's complaints."
      }`,
      affected_segment: "Sample: customers reporting this case",
      recommended_action: "Sample: enable writes (VITE_ENABLE_WRITES=true) to generate a real RCA with the configured LLM.",
      severity: "MEDIUM",
      confidence: 0.5,
      source_evidence: c ? [c.representative_text] : [],
      generated_at: new Date().toISOString(),
      model_used: "sample",
    };
  },
  async reviewQueue(): Promise<ReviewItem[]> {
    await delay();
    return [
      { review_id: 1, complaint_text: "Two-factor login is stuck because the SMS code never shows up.", received_at: iso(1), candidate_case_id: 101, candidate_text: cases[0].representative_text, cosine: 0.52, t_low: 0.4, t_high: 0.55 },
      { review_id: 2, complaint_text: "Everything is painfully slow, loading a single page takes forever.", received_at: iso(2), candidate_case_id: 103, candidate_text: cases[2].representative_text, cosine: 0.54, t_low: 0.4, t_high: 0.55 },
      { review_id: 3, complaint_text: "Wouldn't stop asking for a review", received_at: iso(4), candidate_case_id: 106, candidate_text: cases[5].representative_text, cosine: 0.43, t_low: 0.4, t_high: 0.55 },
    ];
  },
  async submitComplaint(body: ComplaintSubmit): Promise<SubmitResult> {
    await delay(700);
    const text = body.complaint_text.toLowerCase();
    const match = cases.find((c) => c.representative_text.split(" ").filter((w) => w.length > 4 && text.includes(w)).length >= 2);
    return match
      ? { complaint_id: 9001, case_id: match.case_id, is_duplicate: true, status: "Existing case assigned" }
      : { complaint_id: 9002, case_id: 999, is_duplicate: false, status: "New case created" };
  },
  async chat(message: string): Promise<ChatResponse> {
    await delay(600);
    return {
      answer:
        `(sample mode) You asked: "${message}".\n` +
        "Top case right now is #101 – OTP codes not arriving (42 reports, critical spike). " +
        "Its RCA points to the SMS delivery provider.",
    };
  },
};
