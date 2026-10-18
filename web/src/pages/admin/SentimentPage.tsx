import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useCaseTitle, useCases, useTopics } from "../../api/hooks";
import { SentimentBadge } from "../../components/Badges";
import { QueryState } from "../../components/DataState";
import { Card, Kpi, PageHeader } from "../../components/ui";
import { formatNumber, formatPercent, normaliseSentiment, sentimentByTopic, sortBy, summariseSentiment } from "../../lib/format";

const COLORS = { negative: "#e05050", neutral: "#94A3B8", positive: "#1ec58c" };

export function SentimentPage() {
  const cases = useCases();
  const topics = useTopics();
  const navigate = useNavigate();
  const title = useCaseTitle();

  const summary = useMemo(() => summariseSentiment(cases.data ?? []), [cases.data]);
  const byTopic = useMemo(() => sentimentByTopic(cases.data ?? [], topics.data ?? []).slice(0, 8), [cases.data, topics.data]);
  const worst = useMemo(
    () => sortBy((cases.data ?? []).filter((c) => normaliseSentiment(c.sentiment) === "negative"), (c) => c.report_count, "desc").slice(0, 10),
    [cases.data],
  );
  const share = (k: "negative" | "neutral" | "positive") => (summary.totalReports ? summary.reports[k] / summary.totalReports : 0);
  const pie = (["negative", "neutral", "positive"] as const).map((k) => ({ name: k, value: summary.reports[k] }));

  return (
    <div className="stack">
      <PageHeader
        title="Sentiment"
        subtitle="Computed from live case data. Each case counts once per report it has received."
      />
      <QueryState query={cases} loadingLabel="Loading sentiment…" isEmpty={(d) => d.length === 0} empty="No cases yet.">
        {() => (
          <>
            <div className="grid grid-4">
              <Kpi label="Negative" value={formatPercent(share("negative"))} hint={`${formatNumber(summary.reports.negative)} reports`} />
              <Kpi label="Neutral" value={formatPercent(share("neutral"))} hint={`${formatNumber(summary.reports.neutral)} reports`} />
              <Kpi label="Positive" value={formatPercent(share("positive"))} hint={`${formatNumber(summary.reports.positive)} reports`} />
              <Kpi label="Avg. model confidence" value={formatPercent(summary.avgConfidence)} hint={`${formatNumber(summary.totalCases)} cases`} />
            </div>
            <div className="grid grid-2">
              <Card title="Share of reports">
                <div style={{ width: "100%", height: 260 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie data={pie} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={2}>
                        {pie.map((p) => (
                          <Cell key={p.name} fill={COLORS[p.name]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </Card>
              <Card title="Reports by topic and sentiment">
                <div style={{ width: "100%", height: 260 }}>
                  <ResponsiveContainer>
                    <BarChart data={byTopic} layout="vertical" margin={{ left: 8, right: 12 }}>
                      <CartesianGrid stroke="#E2E8F0" horizontal={false} />
                      <XAxis type="number" tick={{ fontSize: 12, fill: "#64748B" }} allowDecimals={false} />
                      <YAxis type="category" dataKey="topic" width={150} tick={{ fontSize: 11, fill: "#64748B" }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="negative" stackId="s" fill={COLORS.negative} />
                      <Bar dataKey="neutral" stackId="s" fill={COLORS.neutral} />
                      <Bar dataKey="positive" stackId="s" fill={COLORS.positive} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            </div>
            <Card title="Most-reported negative cases">
              {worst.length === 0 ? (
                <p className="muted">No negative cases.</p>
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Case</th>
                        <th>Problem</th>
                        <th className="num">Reports</th>
                        <th>Sentiment</th>
                        <th className="num">Confidence</th>
                      </tr>
                    </thead>
                    <tbody>
                      {worst.map((c) => (
                        <tr key={c.case_id} className="clickable" onClick={() => navigate(`/admin/cases/${c.case_id}`)}>
                          <td>#{c.case_id}</td>
                          <td className="clamp-2">{title(c)}</td>
                          <td className="num">{formatNumber(c.report_count)}</td>
                          <td>
                            <SentimentBadge value={c.sentiment} />
                          </td>
                          <td className="num">{formatPercent(c.confidence_score)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              <p className="muted small" style={{ marginBottom: 0 }}>
                Note: case sentiment is currently computed from the case's first complaint only (backend behaviour).
              </p>
            </Card>
          </>
        )}
      </QueryState>
    </div>
  );
}
