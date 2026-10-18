import { useNavigate } from "react-router-dom";
import { useCaseTitle, useGroupSpikes, useOverview, useUnassignedSpikes } from "../../api/hooks";
import { SpikeBadge } from "../../components/Badges";
import { QueryState } from "../../components/DataState";
import { Card, PageHeader } from "../../components/ui";
import { formatChance, formatExpected, formatNumber, sortBy } from "../../lib/format";

// Detector v2 (backend/services/spike_detection.py): a window spikes when it has at least 2 reports
// (3 for alert groups) and that count would happen by chance less than 0.1% of the time given the
// case's own 7-day baseline (Poisson tail with a prior, so new and quiet cases do not alert on one report).

export function IncidentsPage() {
  // /dashboard/overview computes case spikes for all cases with one bulk query.
  const overview = useOverview();
  const groups = useGroupSpikes();
  const vague = useUnassignedSpikes();
  const navigate = useNavigate();
  const title = useCaseTitle();
  const rows = sortBy(overview.data?.spike_cases ?? [], (s) => -(s.p_value ?? 1), "desc");
  const groupRows = groups.data ?? [];
  const vagueRows = (vague.data?.products ?? []).filter((p) => p.spike);
  const critical = rows.filter((s) => s.critical).length;
  const total = rows.length + groupRows.length + vagueRows.length;

  return (
    <div className="stack">
      <PageHeader
        title="Incident Response"
        subtitle="Problems whose reports in the current 6-hour window are far above their usual rate. Three signals: a single case spiking, several related cases spiking together, and a surge of vague complaints that fit no case. Open a case to review its RCA and escalate."
        badges={critical > 0 ? <span className="pill pill-spike">{critical} critical</span> : <span className="pill pill-live">Live</span>}
        stats={[
          { label: "Active incidents", value: formatNumber(total) },
          { label: "Spiking cases", value: formatNumber(rows.length) },
          { label: "Alert groups", value: formatNumber(groupRows.length) },
          { label: "Vague surges", value: formatNumber(vagueRows.length) },
        ]}
      />

      <Card title="Spiking cases">
        <QueryState query={overview} loadingLabel="Running spike detection…" isEmpty={(d) => d.spike_cases.length === 0} empty="No case is spiking right now.">
          {() => (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Case</th>
                    <th>Problem</th>
                    <th className="num">Reports this window</th>
                    <th className="num">Usual per window</th>
                    <th className="num">Chance if normal</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((s) => (
                    <tr key={s.case_id} className="clickable" onClick={() => navigate(`/admin/cases/${s.case_id}`)}>
                      <td>#{s.case_id}</td>
                      <td className="clamp-2">{title(s)}</td>
                      <td className="num">{formatNumber(s.current)}</td>
                      <td className="num">{formatExpected(s.baseline_rate)}</td>
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
        </QueryState>
      </Card>

      <Card title="Alert groups: related cases spiking together">
        <p className="muted small">One problem is sometimes split across similar cases. Their reports are counted together, so the burst is caught even when no single case spikes. The cases themselves stay separate.</p>
        <QueryState query={groups} loadingLabel="Checking alert groups…" isEmpty={(d) => d.length === 0} empty="No alert group is spiking right now.">
          {(d) => (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Cases</th>
                    <th>Problem (first case)</th>
                    <th className="num">Reports this window</th>
                    <th className="num">Chance if normal</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {d.map((g) => (
                    <tr key={String(g.group_id)} className="clickable" onClick={() => navigate(`/admin/cases/${g.case_ids[0]}`)}>
                      <td>{g.case_ids.map((c) => `#${c}`).join(", ")}</td>
                      <td className="clamp-2">{title({ case_id: g.case_ids[0], representative_text: g.representative_texts?.[0] })}</td>
                      <td className="num">{formatNumber(g.current)}</td>
                      <td className="num">{formatChance(g.p_value)}</td>
                      <td>
                        <SpikeBadge spike={g.spike} critical={g.critical} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </QueryState>
      </Card>

      <Card title="Vague-complaint alarm">
        <p className="muted small">Complaints like "the app is not working" are too vague to join any case. They are counted per product, so an outage that customers only describe vaguely still raises an alarm.</p>
        <QueryState
          query={vague}
          loadingLabel="Checking vague complaints…"
          isEmpty={(d) => !d.enabled || d.products.length === 0}
          empty="The vague-complaint alarm is not enabled on this server."
        >
          {(d) => (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th className="num">Vague reports this window</th>
                    <th className="num">Usual per window</th>
                    <th className="num">Chance if normal</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sortBy(d.products, (p) => -(p.p_value ?? 1), "desc").map((p) => (
                    <tr key={p.product}>
                      <td>{p.product}</td>
                      <td className="num">{formatNumber(p.current)}</td>
                      <td className="num">{formatExpected(p.baseline_rate)}</td>
                      <td className="num">{formatChance(p.p_value)}</td>
                      <td>{p.spike ? <SpikeBadge spike={p.spike} critical={p.critical} /> : <span className="muted small">normal</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </QueryState>
      </Card>
    </div>
  );
}
