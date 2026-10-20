import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { friendlyMessage } from "../../api/client";
import { useSubmitComplaint } from "../../api/hooks";
import type { SubmitResult } from "../../api/types";
import { useAuth } from "../../auth/AuthProvider";
import { SampleBadge } from "../../components/SampleBadge";
import { isSample } from "../../config";

// Mirrors backend/models/complaint.py (ComplaintSubmit).
export const LIMITS = { minChars: 10, maxChars: 5000, maxProduct: 200 };

// backend status when the same user repeats a case within 24 hours (counted once)
const REPEAT = "Merged with recent report";

export function validateComplaint(text: string, product: string): string | null {
  const t = text.trim();
  if (t.length < LIMITS.minChars) return `Please describe the problem in at least ${LIMITS.minChars} characters.`;
  if (t.length > LIMITS.maxChars) return `Please keep it under ${LIMITS.maxChars} characters.`;
  if (product.length > LIMITS.maxProduct) return `Product name must be under ${LIMITS.maxProduct} characters.`;
  return null;
}

export function SubmitComplaintPage() {
  const { user, canUseAdmin, signOut } = useAuth();
  const submit = useSubmitComplaint();
  const [text, setText] = useState("");
  const [product, setProduct] = useState("");
  const [rating, setRating] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<(SubmitResult & { text: string })[]>([]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const problem = validateComplaint(text, product);
    if (problem) return setError(problem);
    try {
      const result = await submit.mutateAsync({
        complaint_text: text.trim(),
        product: product.trim() || null,
        rating: rating ? Number(rating) : null,
      });
      setHistory((h) => [{ ...result, text: text.trim() }, ...h].slice(0, 10));
      setText("");
      setRating("");
    } catch (err) {
      setError(friendlyMessage(err));
    }
  }

  const last = history[0];
  return (
    <div className="customer-shell">
      <div className="customer-top">
        <span className="brand">InsightDesk · Support</span>
        <span className="row">
          {canUseAdmin && (
            <Link to="/admin" className="btn btn-ghost">
              Operator dashboard
            </Link>
          )}
          <span className="small" style={{ color: "var(--navy-muted)" }}>{user?.email}</span>
          <button className="btn btn-ghost" type="button" onClick={() => signOut()}>
            Sign out
          </button>
        </span>
      </div>
      <main className="customer-main stack">
        <form className="card stack" onSubmit={onSubmit} noValidate>
          {isSample("submit") && (
            <div className="alert alert-warning small row">
              <SampleBadge /> Submissions are simulated right now – nothing is stored and no case is created.
            </div>
          )}
          <div>
            <h2>Report a problem</h2>
            <p className="muted small">Tell us what went wrong and where. Similar reports from other customers are grouped so the team sees how many people are affected.</p>
          </div>
          <div className="field">
            <label htmlFor="complaint">What happened?</label>
            <textarea
              id="complaint"
              className="textarea"
              value={text}
              maxLength={LIMITS.maxChars}
              placeholder="e.g. I never receive the verification code when I try to log in on the mobile app."
              onChange={(e) => setText(e.target.value)}
            />
            <span className="hint">
              {text.trim().length}/{LIMITS.maxChars} characters
            </span>
          </div>
          <div className="grid grid-2">
            <div className="field">
              <label htmlFor="product">Product (optional)</label>
              <input id="product" className="input" value={product} maxLength={LIMITS.maxProduct} onChange={(e) => setProduct(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="rating">Rating (optional)</label>
              <select id="rating" className="select" value={rating} onChange={(e) => setRating(e.target.value)}>
                <option value="">No rating</option>
                {[1, 2, 3, 4, 5].map((r) => (
                  <option key={r} value={r}>
                    {r} ★
                  </option>
                ))}
              </select>
            </div>
          </div>
          {error && <div className="alert alert-error small" role="alert">{error}</div>}
          <div className="row">
            <button className="btn" type="submit" disabled={submit.isPending}>
              {submit.isPending && <span className="spinner" aria-hidden />}
              {submit.isPending ? "Submitting… (first request can take a minute)" : "Submit complaint"}
            </button>
          </div>
        </form>

        {last && (
          <div className="alert alert-success" role="status">
            Thanks – your report was received.{" "}
            {last.status === REPEAT
              ? `You reported this problem recently, so it was added to case #${last.case_id} without counting you twice.`
              : last.is_duplicate
                ? `Others have reported the same problem; it was added to case #${last.case_id}.`
                : `It opened a new case (#${last.case_id}) for the team.`}
          </div>
        )}

        {history.length > 0 && (
          <section className="card">
            <div className="card-title">
              <h3>Your reports this session</h3>
            </div>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Report</th>
                    <th>Case</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h) => (
                    <tr key={`${h.complaint_id}-${h.text}`}>
                      <td><div className="clamp-2">{h.text}</div></td>
                      <td>#{h.case_id}</td>
                      <td>{h.status === REPEAT ? "Already reported by you" : h.is_duplicate ? "Grouped with similar reports" : "New case"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
