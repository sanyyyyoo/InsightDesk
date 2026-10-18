import { Link } from "react-router-dom";
import { useCaseTitle, useClusters } from "../../api/hooks";
import { SentimentBadge } from "../../components/Badges";
import { QueryState } from "../../components/DataState";
import { Card, PageHeader } from "../../components/ui";
import { formatDateTime, formatNumber, formatPercent } from "../../lib/format";

export function TopicsPage() {
  const clusters = useClusters();
  const title = useCaseTitle();
  const d = clusters.data;
  return (
    <div className="stack">
      <PageHeader
        title="Topics"
        subtitle="BERTopic groups cases into themes and maps each theme to a department."
        stats={
          d
            ? [
                { label: "Topics", value: formatNumber(d.topic_count) },
                { label: "Clustered cases", value: formatNumber(d.case_count) },
                { label: "Outlier rate", value: formatPercent(d.outlier_rate, 1) },
                { label: "Last clustered", value: d.last_clustered_at ? formatDateTime(d.last_clustered_at) : "–" },
              ]
            : []
        }
      />
      <QueryState query={clusters} loadingLabel="Loading topics…" isEmpty={(x) => x.topics.length === 0} empty="No topics yet – clustering has not run.">
        {(data) => (
          <div className="grid grid-2">
            {data.topics.map((t) => (
              <Card
                key={t.topic_id}
                title={
                  <div>
                    <h3>{t.topic_name}</h3>
                    <div className="muted small">{t.department ? `Department: ${t.department}` : "No department mapped"}</div>
                  </div>
                }
                actions={
                  <Link className="badge badge-blue" to={`/admin/cases?topic=${t.topic_id}`}>
                    {formatNumber(t.case_count)} cases →
                  </Link>
                }
              >
                {t.description && <p className="muted small" style={{ marginTop: 0 }}>{t.description}</p>}
                {t.representative_cases.length === 0 ? (
                  <p className="muted small">No cases assigned.</p>
                ) : (
                  <ul style={{ margin: 0, paddingLeft: 0, listStyle: "none" }} className="stack">
                    {t.representative_cases.map((c) => (
                      <li key={c.case_id} className="row between">
                        <Link to={`/admin/cases/${c.case_id}`} className="clamp-2" style={{ flex: 1 }}>
                          #{c.case_id} · {title(c)}
                        </Link>
                        <span className="row">
                          <SentimentBadge value={c.sentiment} />
                          <span className="badge badge-neutral">{formatNumber(c.report_count)}</span>
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </Card>
            ))}
          </div>
        )}
      </QueryState>
    </div>
  );
}
