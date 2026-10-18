import { useNavigate } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useCaseTitle, useOverview } from "../../api/hooks";
import { SpikeBadge } from "../../components/Badges";
import { QueryState } from "../../components/DataState";
import { Card, PageHeader } from "../../components/ui";
import { formatNumber, sortBy } from "../../lib/format";

export function IncidentsPage() {
  // /dashboard/overview computes spikes for all cases with one bulk query;
  // /dashboard/spikes queries case by case and is very slow on large tables.
  const overview = useOverview();
  const navigate = useNavigate();
  const title = useCaseTitle();
  const rows = sortBy(overview.data?.spike_cases ?? [], (s) => s.z_score, "desc");
  const critical = rows.filter((s) => s.critical).length;

  return (
    <div className="stack">
      <PageHeader
        title="Incident Response"
        subtitle="Cases whose report volume in the current 6-hour window is unusually high (z > 2 spike, z > 3 critical). Open a case to review its RCA and escalate."
        badges={critical > 0 ? <span className="pill pill-spike">{critical} critical</span> : <span className="pill pill-live">Live</span>}
        stats={overview.data ? [{ label: "Spiking cases", value: formatNumber(rows.length) }, { label: "Critical", value: formatNumber(critical) }] : []}
      />
      <QueryState query={overview} loadingLabel="Running spike detection…" isEmpty={(d) => d.spike_cases.length === 0} empty="No spiking cases right now.">
        {() => (
          <>
            <Card title="Spike strength by case">
              <div style={{ width: "100%", height: Math.max(180, rows.length * 34) }}>
                <ResponsiveContainer>
                  <BarChart data={rows.map((s) => ({ name: `#${s.case_id}`, z: Number(s.z_score.toFixed(2)), critical: s.critical }))} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <CartesianGrid stroke="#E2E8F0" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 12, fill: "#64748B" }} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 12, fill: "#64748B" }} width={56} />
                    <Tooltip formatter={(v) => [v, "z-score"]} />
                    <ReferenceLine x={2} stroke="#F59E0B" strokeDasharray="4 3" />
                    <ReferenceLine x={3} stroke="#DC2626" strokeDasharray="4 3" />
                    <Bar dataKey="z" radius={[0, 4, 4, 0]}>
                      {rows.map((s) => (
                        <Cell key={s.case_id} fill={s.critical ? "#e05050" : "#F59E0B"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
            <Card title="Spiking cases">
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Case</th>
                      <th>Problem</th>
                      <th className="num">Reports in window</th>
                      <th className="num">z-score</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((s) => (
                      <tr key={s.case_id} className="clickable" onClick={() => navigate(`/admin/cases/${s.case_id}`)}>
                        <td>#{s.case_id}</td>
                        <td className="clamp-2">{title(s)}</td>
                        <td className="num">{formatNumber(s.current)}</td>
                        <td className="num">{s.z_score.toFixed(2)}</td>
                        <td>
                          <SpikeBadge spike={s.spike} critical={s.critical} />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </>
        )}
      </QueryState>
    </div>
  );
}
