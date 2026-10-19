import { Link, useNavigate } from "react-router-dom";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useCaseTitle, useOverview } from "../../api/hooks";
import { SpikeBadge } from "../../components/Badges";
import { QueryState } from "../../components/DataState";
import { Card, PageHeader } from "../../components/ui";
import { formatChance, formatNumber, sortBy, volumeSeries } from "../../lib/format";

export function OverviewPage() {
  const overview = useOverview();
  const navigate = useNavigate();
  const title = useCaseTitle();
  const d = overview.data;

  return (
    <div className="stack">
      <PageHeader
        title="Overview"
        subtitle="Complaints grouped into problem-level cases, with live spike detection."
        badges={
          <>
            <span className="pill pill-live">Live</span>
            {d && d.spikes > 0 && <span className="pill pill-spike">{d.spikes} spiking</span>}
          </>
        }
        stats={
          d
            ? [
                { label: "Complaints", value: formatNumber(d.complaints) },
                { label: "Cases", value: formatNumber(d.cases) },
                { label: "Topics", value: formatNumber(d.topics) },
                { label: "Spiking cases", value: formatNumber(d.spikes) },
              ]
            : []
        }
      />

      <QueryState query={overview} loadingLabel="Loading overview…">
        {(data) => (
          <>
            <Card title={data.volume_by_day.length > 0 && volumeSeries(data.volume_by_day)[0]?.key.length === 7 ? "Complaint volume by month" : "Complaint volume by day"}>
              {data.volume_by_day.length === 0 ? (
                <p className="muted">No complaints yet.</p>
              ) : (
                <div style={{ width: "100%", height: 260 }}>
                  <ResponsiveContainer>
                    <AreaChart data={volumeSeries(data.volume_by_day)} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="vol" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#2563EB" stopOpacity={0.35} />
                          <stop offset="95%" stopColor="#2563EB" stopOpacity={0.02} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#E2E8F0" vertical={false} />
                      <XAxis dataKey="label" tick={{ fontSize: 12, fill: "#64748B" }} minTickGap={16} />
                      <YAxis tick={{ fontSize: 12, fill: "#64748B" }} allowDecimals={false} width={36} />
                      <Tooltip formatter={(v) => [v, "Complaints"]} labelFormatter={(l) => String(l)} />
                      <Area type="monotone" dataKey="count" stroke="#2563EB" strokeWidth={2} fill="url(#vol)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </Card>

            <Card
              title="Spiking cases"
              actions={
                <Link to="/admin/incidents" className="small">
                  Incident response →
                </Link>
              }
            >
              {data.spike_cases.length === 0 ? (
                <p className="muted">No spikes right now.</p>
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Case</th>
                        <th>Problem</th>
                        <th className="num">Reports now</th>
                        <th className="num">Chance if normal</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortBy(data.spike_cases, (s) => -(s.p_value ?? 1), "desc").map((s) => (
                        <tr key={s.case_id} className="clickable" onClick={() => navigate(`/admin/cases/${s.case_id}`)}>
                          <td>#{s.case_id}</td>
                          <td><div className="clamp-2">{title(s)}</div></td>
                          <td className="num">{formatNumber(s.current)}</td>
                          <td className="num">{formatChance(s.p_value)}</td>
                          <td>
                            <SpikeBadge spike={s.spike} critical={s.critical} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </>
        )}
      </QueryState>
    </div>
  );
}
