import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useCaseTitle, useCases, useTopics } from "../../api/hooks";
import type { Case } from "../../api/types";
import { SentimentBadge } from "../../components/Badges";
import { QueryState } from "../../components/DataState";
import { Card, PageHeader } from "../../components/ui";
import { formatNumber, normaliseSentiment, sortBy, timeAgo, type SortDir } from "../../lib/format";

type SortKey = "case_id" | "report_count" | "last_reported_at" | "sentiment";
const PAGE_SIZE = 25;

export function CasesPage() {
  const cases = useCases();
  const title = useCaseTitle();
  const topics = useTopics();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const q = params.get("q") ?? "";
  const sentiment = params.get("sentiment") ?? "all";
  const topic = params.get("topic") ?? "all";
  const [sort, setSort] = useState<{ key: SortKey; dir: SortDir }>({ key: "report_count", dir: "desc" });
  const [page, setPage] = useState(0);

  const topicName = useMemo(() => new Map((topics.data ?? []).map((t) => [t.topic_id, t.topic_name])), [topics.data]);

  function update(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (!value || value === "all") next.delete(key);
    else next.set(key, value);
    setParams(next, { replace: true });
    setPage(0);
  }

  function toggleSort(key: SortKey) {
    setSort((s) => ({ key, dir: s.key === key && s.dir === "desc" ? "asc" : "desc" }));
  }

  const filtered = useMemo(() => {
    const term = q.trim().toLowerCase();
    let rows: Case[] = cases.data ?? [];
    if (term) rows = rows.filter((c) => title(c).toLowerCase().includes(term) || String(c.case_id) === term);
    if (sentiment !== "all") rows = rows.filter((c) => normaliseSentiment(c.sentiment) === sentiment);
    if (topic !== "all") rows = rows.filter((c) => String(c.topic_id ?? "none") === topic);
    const key = (c: Case) =>
      sort.key === "last_reported_at" ? new Date(c.last_reported_at).getTime() : sort.key === "sentiment" ? normaliseSentiment(c.sentiment) : c[sort.key];
    return sortBy(rows, key, sort.dir);
  }, [cases.data, q, sentiment, topic, sort, title]);

  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const current = Math.min(page, pages - 1);
  const visible = filtered.slice(current * PAGE_SIZE, current * PAGE_SIZE + PAGE_SIZE);
  const arrow = (k: SortKey) => (sort.key === k ? (sort.dir === "desc" ? " ▼" : " ▲") : "");

  return (
    <div className="stack">
      <PageHeader title="Cases" subtitle="Each case groups duplicate complaints about one problem. Click a case for its complaints, spike status and root-cause analysis." />
      <Card>
        <div className="row" style={{ marginBottom: 12 }}>
          <input
            className="input"
            style={{ maxWidth: 320 }}
            placeholder="Search problem text or case #"
            aria-label="Search cases"
            value={q}
            onChange={(e) => update("q", e.target.value)}
          />
          <select className="select" style={{ maxWidth: 180 }} aria-label="Filter by sentiment" value={sentiment} onChange={(e) => update("sentiment", e.target.value)}>
            <option value="all">All sentiment</option>
            <option value="negative">Negative</option>
            <option value="neutral">Neutral</option>
            <option value="positive">Positive</option>
          </select>
          <select className="select" style={{ maxWidth: 240 }} aria-label="Filter by topic" value={topic} onChange={(e) => update("topic", e.target.value)}>
            <option value="all">All topics</option>
            {(topics.data ?? []).map((t) => (
              <option key={t.topic_id} value={t.topic_id}>
                {t.topic_name}
              </option>
            ))}
            <option value="none">Unassigned</option>
          </select>
          <span className="muted small">{formatNumber(filtered.length)} cases</span>
        </div>
        <QueryState query={cases} loadingLabel="Loading cases…" isEmpty={(d) => d.length === 0} empty="No cases yet.">
          {() =>
            filtered.length === 0 ? (
              <p className="muted">No cases match these filters.</p>
            ) : (
              <>
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th className="sortable" onClick={() => toggleSort("case_id")}>Case{arrow("case_id")}</th>
                        <th>Problem (founder complaint)</th>
                        <th>Topic</th>
                        <th className="sortable num" onClick={() => toggleSort("report_count")}>Reports{arrow("report_count")}</th>
                        <th className="sortable" onClick={() => toggleSort("sentiment")}>Sentiment{arrow("sentiment")}</th>
                        <th className="sortable" onClick={() => toggleSort("last_reported_at")}>Last report{arrow("last_reported_at")}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {visible.map((c) => (
                        <tr key={c.case_id} className="clickable" onClick={() => navigate(`/admin/cases/${c.case_id}`)}>
                          <td>#{c.case_id}</td>
                          <td><div className="clamp-2">{title(c)}</div></td>
                          <td className="small">{(c.topic_id != null && topicName.get(c.topic_id)) || "–"}</td>
                          <td className="num">{formatNumber(c.report_count)}</td>
                          <td>
                            <SentimentBadge value={c.sentiment} />
                          </td>
                          <td className="small">{timeAgo(c.last_reported_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {pages > 1 && (
                  <div className="row between mt">
                    <button className="btn btn-secondary" type="button" disabled={current === 0} onClick={() => setPage(current - 1)}>
                      ← Previous
                    </button>
                    <span className="muted small">
                      Page {current + 1} of {pages}
                    </span>
                    <button className="btn btn-secondary" type="button" disabled={current >= pages - 1} onClick={() => setPage(current + 1)}>
                      Next →
                    </button>
                  </div>
                )}
              </>
            )
          }
        </QueryState>
      </Card>
    </div>
  );
}
