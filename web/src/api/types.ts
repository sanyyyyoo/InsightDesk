// Shapes returned by the FastAPI backend (backend/routers/*.py,
// backend/database/schema.sql). Optional fields may be null in Supabase.

export type Sentiment = "positive" | "negative" | "neutral" | string;

export interface Case {
  case_id: number;
  representative_text: string;
  report_count: number;
  user_ids?: string[];
  topic_id?: number | null;
  sentiment?: Sentiment | null;
  confidence_score?: number | null;
  sentiment_model?: string | null;
  emotion?: string | null;
  emotion_confidence?: number | null;
  spike_status?: boolean | null;
  spike_score?: number | null;
  spike_detected_at?: string | null;
  created_at: string;
  last_reported_at: string;
}

export interface Complaint {
  complaint_id: number;
  complaint_text: string;
  cleaned_text?: string | null;
  user_id: string;
  rating?: number | null;
  source?: string | null;
  product?: string | null;
  company_size?: string | null;
  is_synthetic?: boolean;
  case_id?: number | null;
  is_duplicate?: boolean;
  created_at: string;
}

export interface Topic {
  topic_id: number;
  topic_name: string;
  topic_slug?: string;
  department?: string | null;
  department_override?: string | null;
  description?: string | null;
}

export interface SpikeResult {
  spike: boolean;
  critical: boolean;
  z_score: number;
  current: number;
}

export interface SpikeCase extends SpikeResult {
  case_id: number;
  representative_text?: string | null;
}

export interface Benchmark {
  benchmark_id?: number;
  model_name: string;
  complaints_processed?: number | null;
  average_latency_ms?: number | null;
  throughput?: number | null;
  memory_mb?: number | null;
  created_at?: string;
}

export interface VolumePoint {
  date: string;
  label: string;
  count: number;
}

export interface Overview {
  complaints: number;
  cases: number;
  topics: number;
  spikes: number;
  spike_cases: SpikeCase[];
  benchmarks: Benchmark[];
  topics_data: Topic[];
  volume_by_day: VolumePoint[];
}

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL" | string;

export interface Rca {
  rca_id?: number;
  case_id: number;
  probable_cause: string;
  affected_segment?: string | null;
  recommended_action?: string | null;
  severity?: Severity | null;
  confidence?: number | null;
  source_evidence?: string[] | null;
  generated_at?: string;
  model_used?: string | null;
}

export interface CaseIntelligence {
  case: Case;
  complaints: Complaint[];
  topic: Topic | null;
  spike: SpikeResult;
  rca: Rca | null;
}

export interface ClusterTopic {
  topic_id: number;
  topic_name: string;
  department?: string | null;
  description?: string | null;
  case_count: number;
  representative_cases: Pick<Case, "case_id" | "representative_text" | "sentiment" | "report_count">[];
}

export interface Clusters {
  case_count: number;
  topic_count: number;
  outlier_count: number;
  outlier_rate: number;
  clustering_version: number;
  last_clustered_at?: string | null;
  topics: ClusterTopic[];
}

export interface EscalateResponse {
  status: string;
  case_id: number;
  message: string;
}

export interface ComplaintSubmit {
  complaint_text: string;
  rating?: number | null;
  product?: string | null;
}

export interface SubmitResult {
  complaint_id: number;
  case_id: number;
  is_duplicate: boolean;
  status: string;
}

export interface ChatResponse {
  answer: string;
}

/** v2 pipeline: a complaint whose best cosine match fell in the uncertain band. */
export interface ReviewItem {
  review_id: number;
  complaint_text: string;
  received_at: string;
  candidate_case_id: number;
  candidate_text: string;
  cosine: number;
  t_low: number;
  t_high: number;
}

/** case_id -> original text of the case's first complaint (GET /dashboard/case-texts). */
export type CaseTexts = Record<string, string>;
