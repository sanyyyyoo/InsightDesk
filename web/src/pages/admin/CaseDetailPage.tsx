import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { friendlyMessage } from "../../api/client";
import { useCaseIntelligence, useCaseTitle, useEscalate, useGenerateRca } from "../../api/hooks";
import type { Rca } from "../../api/types";
import { SentimentBadge, SeverityBadge, SpikeBadge } from "../../components/Badges";
import { ConfirmDialog } from "../../components/ConfirmDialog";
import { QueryState } from "../../components/DataState";
import { SampleBadge } from "../../components/SampleBadge";
import { useToast } from "../../components/Toast";
import { isSample } from "../../config";
import { Card, Kpi, PageHeader } from "../../components/ui";
import { formatDateTime, formatNumber, formatPercent, sortBy, timeAgo } from "../../lib/format";

export function CaseDetailPage() {
  const { caseId } = useParams();
  const id = Number(caseId);
  const valid = Number.isInteger(id) && id > 0;
  const intel = useCaseIntelligence(valid ? id : null);
  const escalate = useEscalate();
  const generate = useGenerateRca();
  const title = useCaseTitle();
  const toast = useToast();
  const [confirming, setConfirming] = useState(false);
  const [confirmRegen, setConfirmRegen] = useState(false);
  const [escalateError, setEscalateError] = useState<string | null>(null);
  const [rcaError, setRcaError] = useState<string | null>(null);
  // Sample-mode RCAs are not saved, so keep the returned one on screen.
  const [sampleRca, setSampleRca] = useState<Rca | null>(null);
  const rcaSample = isSample("generateRca");
  const escalateSample = isSample("escalate");

  if (!valid) {
    return (
      <div className="card stack">
        <h3>Invalid case number</h3>
        <Link to="/admin/cases">← Back to cases</Link>
      </div>
    );
  }

  async function doGenerate(force: boolean) {
    setRcaError(null);
    try {
      const result = await generate.mutateAsync({ caseId: id, force });
      if (rcaSample) setSampleRca(result);
      toast(rcaSample ? "Sample RCA shown – nothing was generated or saved." : `RCA ${force ? "regenerated" : "generated"} for case #${id}.`);
      setConfirmRegen(false);
    } catch (err) {
      setRcaError(friendlyMessage(err));
      setConfirmRegen(false);
    }
  }

  async function doEscalate() {
    setEscalateError(null);
    try {
      const res = await escalate.mutateAsync(id);
      toast(res.message || `Case #${id} escalated.`);
      setConfirming(false);
    } catch (err) {
      setEscalateError(friendlyMessage(err));
    }
  }

  return (
    <div className="stack">
      <div>
        <Link to="/admin/cases" className="small">
          ← All cases
        </Link>
      </div>
      <QueryState query={intel} loadingLabel={`Loading case #${id}…`}>
        {({ case: c, complaints, topic, spike, rca: liveRca }) => {
          const rca = liveRca ?? (sampleRca && sampleRca.case_id === c.case_id ? sampleRca : null);
          const rcaIsSample = !liveRca && rca !== null;
          return (
          <>
            <PageHeader
              title={`Case #${c.case_id}`}
              subtitle={title(c)}
              badges={<SpikeBadge spike={spike.spike} critical={spike.critical} />}
              stats={[
                { label: "Reports", value: formatNumber(c.report_count) },
                { label: "Spike z-score", value: spike.z_score.toFixed(2) },
                { label: "Current 6-h window", value: formatNumber(spike.current) },
                { label: "Last report", value: timeAgo(c.last_reported_at) },
              ]}
            />

            <div className="grid grid-3">
              <Kpi label="Topic" value={<span style={{ fontSize: 16 }}>{topic?.topic_name ?? "Unassigned"}</span>} hint={topic?.department ? `Department: ${topic.department}` : undefined} />
              <Kpi
                label="Sentiment"
                value={<SentimentBadge value={c.sentiment} />}
                hint={typeof c.confidence_score === "number" ? `Confidence ${formatPercent(c.confidence_score)} · ${c.sentiment_model ?? ""}` : undefined}
              />
              <Kpi label="First reported" value={<span style={{ fontSize: 16 }}>{formatDateTime(c.created_at)}</span>} />
            </div>

            <Card
              title={
                <h3 className="row">
                  Root-cause analysis {rcaIsSample && <SampleBadge />}
                </h3>
              }
              actions={
                <div className="row">
                  <button
                    className="btn btn-secondary"
                    type="button"
                    disabled={generate.isPending}
                    onClick={() => (liveRca ? setConfirmRegen(true) : doGenerate(false))}
                    title={rcaSample ? "Sample mode: shows an example RCA; nothing is generated or saved" : "Calls the LLM once for this case"}
                  >
                    {generate.isPending && <span className="spinner" aria-hidden />}
                    {liveRca ? "Regenerate RCA" : "Generate RCA"} {rcaSample && <SampleBadge />}
                  </button>
                  <button className="btn btn-danger" type="button" disabled={!rca} title={rca ? undefined : "Generate an RCA before escalating"} onClick={() => setConfirming(true)}>
                    Escalate {escalateSample && <SampleBadge />}
                  </button>
                </div>
              }
            >
              {rcaError && (
                <div className="alert alert-error small" role="alert" style={{ marginBottom: 10 }}>
                  {rcaError}
                </div>
              )}
              {generate.isPending && !rca ? (
                <p className="muted row">
                  <span className="spinner" aria-hidden /> Generating root-cause analysis…
                </p>
              ) : rca ? (
                <div className="stack">
                  <div className="row">
                    <SeverityBadge value={rca.severity} />
                    {typeof rca.confidence === "number" && <span className="badge badge-blue">Confidence {formatPercent(rca.confidence)}</span>}
                    <span className="muted small">
                      {rca.model_used ?? "LLM"} · {formatDateTime(rca.generated_at)}
                    </span>
                  </div>
                  <div>
                    <b>Probable cause</b>
                    <p style={{ margin: "4px 0 0" }}>{rca.probable_cause}</p>
                  </div>
                  {rca.affected_segment && (
                    <div>
                      <b>Affected segment</b>
                      <p style={{ margin: "4px 0 0" }}>{rca.affected_segment}</p>
                    </div>
                  )}
                  {rca.recommended_action && (
                    <div>
                      <b>Recommended action</b>
                      <p style={{ margin: "4px 0 0" }}>{rca.recommended_action}</p>
                    </div>
                  )}
                  {rca.source_evidence && rca.source_evidence.length > 0 && (
                    <div>
                      <b>Evidence</b>
                      <ul style={{ margin: "4px 0 0", paddingLeft: 18 }}>
                        {rca.source_evidence.map((e, i) => (
                          <li key={i}>{e}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <p className="muted">No root-cause analysis yet. RCAs are only generated when you click <b>Generate RCA</b>; escalation needs one.</p>
              )}
            </Card>

            <Card title={`Complaints in this case (${complaints.length})`}>
              {complaints.length === 0 ? (
                <p className="muted">No complaints linked.</p>
              ) : (
                <div className="table-wrap">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Complaint</th>
                        <th>Source</th>
                        <th className="num">Rating</th>
                        <th>Received</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortBy(complaints, (x) => new Date(x.created_at).getTime(), "desc").map((x) => (
                        <tr key={x.complaint_id}>
                          <td>{x.complaint_id}</td>
                          <td>{x.complaint_text}</td>
                          <td className="small">{x.source ?? "–"}</td>
                          <td className="num">{x.rating ?? "–"}</td>
                          <td className="small">{formatDateTime(x.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>

            <ConfirmDialog
              open={confirming}
              title={`Escalate case #${c.case_id}?`}
              confirmLabel="Send escalation email"
              danger
              busy={escalate.isPending}
              onConfirm={doEscalate}
              onCancel={() => {
                setConfirming(false);
                setEscalateError(null);
              }}
            >
              {escalateSample && (
                <div className="alert alert-warning small">Sample mode: the escalation is simulated – no email is sent.</div>
              )}
              <p style={{ margin: 0 }}>
                This emails the responsible department ({topic?.department ?? "mapped from the topic"}) with the RCA and evidence. It cannot be undone.
              </p>
              {rca && (
                <div className="alert alert-info small">
                  <SeverityBadge value={rca.severity} /> {rca.probable_cause}
                </div>
              )}
              {escalateError && (
                <div className="alert alert-error small" role="alert">
                  {escalateError}
                </div>
              )}
            </ConfirmDialog>
            <ConfirmDialog
              open={confirmRegen}
              title={`Regenerate the RCA for case #${c.case_id}?`}
              confirmLabel="Regenerate"
              busy={generate.isPending}
              onConfirm={() => doGenerate(true)}
              onCancel={() => setConfirmRegen(false)}
            >
              <p style={{ margin: 0 }}>
                {rcaSample
                  ? "Sample mode: an example RCA is shown; nothing is generated or saved."
                  : "This makes a new LLM call and saves a new RCA row for this case. The previous RCA stays in the history."}
              </p>
            </ConfirmDialog>
          </>
          );
        }}
      </QueryState>
    </div>
  );
}
