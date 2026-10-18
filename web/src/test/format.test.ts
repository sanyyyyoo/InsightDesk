import type { Case } from "../api/types";
import { formatPercent, normaliseSentiment, sentimentByTopic, sortBy, summariseSentiment, timeAgo, volumeSeries } from "../lib/format";

const mk = (id: number, sentiment: string | null, reports: number, topic: number | null = 1, conf: number | null = 0.8): Case => ({
  case_id: id,
  representative_text: `case ${id}`,
  report_count: reports,
  sentiment,
  topic_id: topic,
  confidence_score: conf,
  created_at: "2026-01-01T00:00:00Z",
  last_reported_at: "2026-01-01T00:00:00Z",
});

describe("format helpers", () => {
  it("normalises sentiment labels from different models", () => {
    expect(normaliseSentiment("NEGATIVE")).toBe("negative");
    expect(normaliseSentiment("Pos")).toBe("positive");
    expect(normaliseSentiment("neutral")).toBe("neutral");
    expect(normaliseSentiment(null)).toBe("unknown");
  });

  it("weights sentiment by report count and averages confidence", () => {
    const s = summariseSentiment([mk(1, "negative", 10), mk(2, "positive", 2), mk(3, null, 0, 1, null)]);
    expect(s.cases).toEqual({ positive: 1, negative: 1, neutral: 0, unknown: 1 });
    expect(s.reports.negative).toBe(10);
    expect(s.reports.unknown).toBe(1); // zero reports still counts the case once
    expect(s.totalReports).toBe(13);
    expect(s.avgConfidence).toBeCloseTo(0.8);
  });

  it("groups sentiment by topic and puts unassigned cases in their own row", () => {
    const rows = sentimentByTopic([mk(1, "negative", 5, 1), mk(2, "positive", 1, null)], [{ topic_id: 1, topic_name: "Login" }]);
    expect(rows[0]).toEqual({ topic: "Login", positive: 0, neutral: 0, negative: 5 });
    expect(rows[1].topic).toBe("Unassigned");
  });

  it("sorts with nulls last in both directions", () => {
    const rows = [{ v: 2 }, { v: null }, { v: 5 }];
    expect(sortBy(rows, (r) => r.v, "desc").map((r) => r.v)).toEqual([5, 2, null]);
    expect(sortBy(rows, (r) => r.v, "asc").map((r) => r.v)).toEqual([2, 5, null]);
  });

  it("formats percentages and relative times defensively", () => {
    expect(formatPercent(0.256)).toBe("26%");
    expect(formatPercent(null)).toBe("–");
    const now = Date.parse("2026-01-02T00:00:00Z");
    expect(timeAgo("2026-01-01T23:01:00Z", now)).toBe("59 min ago");
    expect(timeAgo("2026-01-01T22:00:00Z", now)).toBe("2 h ago");
    expect(timeAgo("not a date", now)).toBe("–");
  });

  it("keeps daily points for short spans and groups long spans by month", () => {
    const short = volumeSeries([{ date: "2026-03-02", count: 2 }, { date: "2026-03-01", count: 1 }]);
    expect(short.map((b) => b.label)).toEqual(["01/03", "02/03"]); // sorted, day/month
    const long = volumeSeries([
      { date: "2014-09-06", count: 1 },
      { date: "2026-03-01", count: 4 },
      { date: "2026-03-20", count: 6 },
    ]);
    expect(long).toEqual([
      { key: "2014-09", label: "Sep 14", count: 1 },
      { key: "2026-03", label: "Mar 26", count: 10 },
    ]);
    expect(volumeSeries([{ date: "bad", count: 3 }])).toEqual([]);
  });
});
