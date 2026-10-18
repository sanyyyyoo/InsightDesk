import { useState } from "react";
import { Link } from "react-router-dom";
import { useReviewQueue } from "../../api/hooks";
import { QueryState } from "../../components/DataState";
import { SampleBadge } from "../../components/SampleBadge";
import { useToast } from "../../components/Toast";
import { Card, PageHeader } from "../../components/ui";
import { timeAgo } from "../../lib/format";

/**
 * v2 pipeline preview: complaints whose best cosine match fell between
 * t_low and t_high wait here for an operator decision. No backend
 * endpoint exists yet, so this page always uses sample data.
 */
export function ReviewQueuePage() {
  const queue = useReviewQueue();
  const toast = useToast();
  const [done, setDone] = useState<Record<number, "merged" | "new">>({});

  function decide(id: number, decision: "merged" | "new") {
    setDone((d) => ({ ...d, [id]: decision }));
    toast(`Sample: decision "${decision === "merged" ? "same problem" : "new case"}" recorded locally only.`);
  }

  return (
    <div className="stack">
      <PageHeader
        title="Review Queue"
        badges={<SampleBadge title="Preview of the v2 pipeline – not connected to the backend yet" />}
        subtitle="v2 pipeline preview. Clear matches merge automatically and clear non-matches open a new case; only uncertain complaints (cosine between t_low and t_high) wait here for an operator."
      />
      <div className="alert alert-warning small">
        Preview only: the v2 dedup pipeline is not deployed yet and its thresholds will be tuned on the team-labelled Play Store reviews. Decisions here are not saved.
      </div>
      <QueryState query={queue} isEmpty={(d) => d.length === 0} empty="Nothing waiting for review.">
        {(items) => (
          <div className="stack">
            {items.map((it) => (
              <Card
                key={it.review_id}
                title={
                  <div className="row">
                    <span className="badge badge-blue">cosine {it.cosine.toFixed(2)}</span>
                    <span className="muted small">
                      band [{it.t_low.toFixed(2)}, {it.t_high.toFixed(2)}) · received {timeAgo(it.received_at)}
                    </span>
                  </div>
                }
              >
                <div className="grid grid-2">
                  <div>
                    <div className="muted small">New complaint</div>
                    <p style={{ margin: "4px 0 0" }}>{it.complaint_text}</p>
                  </div>
                  <div>
                    <div className="muted small">
                      Closest case <Link to={`/admin/cases/${it.candidate_case_id}`}>#{it.candidate_case_id}</Link> (founder complaint)
                    </div>
                    <p style={{ margin: "4px 0 0" }}>{it.candidate_text}</p>
                  </div>
                </div>
                <div className="row mt">
                  {done[it.review_id] ? (
                    <span className="badge badge-success">{done[it.review_id] === "merged" ? "Marked: same problem" : "Marked: new case"}</span>
                  ) : (
                    <>
                      <button className="btn" type="button" onClick={() => decide(it.review_id, "merged")}>
                        Same problem – merge
                      </button>
                      <button className="btn btn-secondary" type="button" onClick={() => decide(it.review_id, "new")}>
                        Different – new case
                      </button>
                    </>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </QueryState>
    </div>
  );
}
