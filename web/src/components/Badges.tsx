import { normaliseSentiment } from "../lib/format";

export function SentimentBadge({ value }: { value?: string | null }) {
  const s = normaliseSentiment(value);
  const cls = { positive: "badge-success", negative: "badge-danger", neutral: "badge-neutral", unknown: "badge-neutral" }[s];
  return <span className={`badge ${cls}`}>{s === "unknown" ? "–" : s}</span>;
}

export function SeverityBadge({ value }: { value?: string | null }) {
  const v = (value ?? "").toUpperCase();
  const cls =
    v === "CRITICAL" ? "badge-critical" : v === "HIGH" ? "badge-danger" : v === "MEDIUM" ? "badge-warning" : v === "LOW" ? "badge-blue" : "badge-neutral";
  return <span className={`badge ${cls}`}>{v || "–"}</span>;
}

export function SpikeBadge({ spike, critical }: { spike?: boolean; critical?: boolean }) {
  if (critical) return <span className="pill pill-spike">Critical spike</span>;
  if (spike) return <span className="badge badge-warning">Spike</span>;
  return <span className="badge badge-neutral">Normal</span>;
}
