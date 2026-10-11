import os
from dataclasses import dataclass
from datetime import datetime, timezone

from backend.database.supabase import (
    get_case,
    get_rca,
    get_topic,
    get_complaints_by_case,
    save_rca,
)

from backend.services.spike_detection import detect_spike

from backend.llm.provider import (
    generate_json,
    get_model_name,
    get_provider,
)


@dataclass
class RCAResult:
    probable_cause: str
    affected_segment: str
    recommended_action: str
    severity: str
    confidence: float
    source_evidence: list[str]
    generated_at: str
    model_used: str


def fetch_rca_context(case_id):
    case = get_case(case_id)

    if not case:
        raise ValueError(
            f"Case {case_id} not found."
        )

    complaints = get_complaints_by_case(
        case_id
    )

    spike = detect_spike(
        case_id
    )

    if case.get("topic_id") is not None:
        topic = get_topic(
            case["topic_id"]
        )
    else:
        topic = {
            "topic_name": "Unknown",
            "department": "General Support",
        }

    sentiment = {
        "sentiment": case.get(
            "sentiment"
        ),
        "confidence": case.get(
            "confidence_score"
        ),
        "model": case.get(
            "sentiment_model"
        ),
    }

    return {
        "case": case,
        "complaints": complaints[-5:],
        # v2 evidence: first complaint in its original wording + up to 7 more, oldest first
        "evidence": _evidence(complaints),
        "topic": topic,
        "spike": spike,
        "sentiment": sentiment,
    }


# "v3" (default since 2026-10-11, passed reports/replay/rca_v3_rule.md), "v2" or "v1" (original)
RCA_PROMPT_VERSION = os.getenv("RCA_PROMPT_VERSION", "v3").lower()


def _evidence(complaints, limit=8):
    """The case's first complaint (original wording) plus up to limit-1 more, oldest first."""
    rows = sorted(
        complaints,
        key=lambda c: (str(c.get("created_at") or ""), c.get("complaint_id") or 0),
    )
    if len(rows) > limit:
        rows = rows[:1] + rows[-(limit - 1):]
    return [
        (c.get("complaint_text") or c.get("text") or "").strip()
        for c in rows
    ]


def build_prompt(context):
    if RCA_PROMPT_VERSION == "v3":
        return build_prompt_v3(context)
    if RCA_PROMPT_VERSION == "v2":
        return build_prompt_v2(context)
    return build_prompt_v1(context)


def build_prompt_v2(context):
    evidence = "\n".join(
        f"[{n}] {t}" for n, t in enumerate(context.get("evidence") or [], 1)
    )
    spike = context["spike"]
    spike_line = (
        "yes (critical)" if spike.get("critical")
        else "yes" if spike.get("spike") else "no"
    )

    return f"""
You are the Root Cause Analysis component of InsightDesk. A support team will
use your answer to decide what to investigate. Customer complaints describe
SYMPTOMS; they rarely prove a cause. Your job is to state the most likely cause
as a hypothesis, tied to the evidence, and the next steps that follow from it.

Rules:
1. probable_cause: start with "Likely:" and describe the cause as a hypothesis.
   Name only features, behaviours and timings that the complaints mention.
   Do not state a cause as certain. Do not mention a platform, version, component,
   update or date unless a complaint mentions it. End with the supporting
   complaint numbers, e.g. "(complaints 1, 3, 4)".
2. recommended_action: concrete steps to investigate and fix the REPORTED symptom
   (what to reproduce, check or log). No new features unless the complaints ask
   for them. If other problems appear in the complaints, add them at the end as
   "Also reported (separate): ..." instead of folding them into the cause.
3. affected_segment: who is affected, only as far as the complaints say.
4. source_evidence: short quotes from the complaints that support the cause.
5. confidence: 0.0-1.0, lower when complaints are vague or disagree.
   severity: exactly one of LOW, MEDIUM, HIGH, CRITICAL.

Return ONLY one valid JSON object, no markdown:
{{
    "probable_cause": "string",
    "affected_segment": "string",
    "recommended_action": "string",
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "confidence": 0.0,
    "source_evidence": ["string"]
}}

CASE EVIDENCE
Complaints (first one = the complaint that started the case):
{evidence}

Department: {context["topic"]["department"]}
Complaints in the latest 6-hour window: {spike.get("current")}
Normal rate per 6-hour window (last 7 days): {spike.get("baseline_rate", "unknown")}
Spike detected: {spike_line}
""".strip()


V3_RULES_OLD = """Rules:
1. probable_cause: start with "Likely:" and describe the cause as a hypothesis.
   Name only features, behaviours and timings that the complaints mention.
   Do not state a cause as certain. Do not mention a platform, version, component,
   update or date unless a complaint mentions it. End with the supporting
   complaint numbers, e.g. "(complaints 1, 3, 4)".
2. recommended_action: concrete steps to investigate and fix the REPORTED symptom
   (what to reproduce, check or log). No new features unless the complaints ask
   for them. If other problems appear in the complaints, add them at the end as
   "Also reported (separate): ..." instead of folding them into the cause.
3. affected_segment: who is affected, only as far as the complaints say."""

V3_RULES_NEW = """Rules:
1. probable_cause: start with "Likely:" and give ONE hypothesis about the ONE
   symptom that most complaints share (the main problem). Do not combine other
   symptoms into it, even if they appear in the same complaints. Do not state a
   cause as certain. End with the numbers of the complaints that report THIS
   symptom, e.g. "(complaints 1, 3, 4)".
2. If most complaints ask for something the product does not have (a missing
   feature or option), the probable_cause is "Likely: feature request - ..." and
   the recommended_action is product / backlog work, not debugging.
3. Never add an impact, consequence, device, component, version, update or date
   that no complaint states.
4. recommended_action: concrete steps to investigate and fix the MAIN symptom
   (what to reproduce, check or log). Then list every other problem found in the
   complaints at the end as "Also reported (separate): ...".
5. affected_segment: who is affected, only as far as the complaints say."""


def build_prompt_v3(context):
    """v2 + main-symptom-only cause, feature requests, no invented details (reports/replay/rca_v3_rule.md)."""
    p = build_prompt_v2(context)
    assert V3_RULES_OLD in p
    p = p.replace(V3_RULES_OLD, V3_RULES_NEW)
    return p.replace("4. source_evidence:", "6. source_evidence:").replace("5. confidence:", "7. confidence:")


def build_prompt_v1(context):
    complaints = []

    for complaint in context["complaints"]:
        text = (
            complaint.get("text")
            or complaint.get("complaint_text")
            or complaint.get("content")
            or str(complaint)
        )

        complaints.append(
            f"- {text}"
        )

    complaint_text = "\n".join(
        complaints
    )

    return f"""
You are the Root Cause Analysis component of InsightDesk,
a SaaS complaint intelligence system.

Analyze ONLY the evidence supplied below.

Do not invent outages, infrastructure failures, geographic
effects, affected products, or technical causes that are not
supported by the evidence.

If the evidence is insufficient to identify an exact technical
cause, state the most plausible complaint-level cause and keep
confidence appropriately low.

Severity must be exactly one of:
LOW, MEDIUM, HIGH, CRITICAL

Confidence must be a NUMBER between 0.0 and 1.0.

Return ONLY one valid JSON object.
Do not use markdown.
Do not include reasoning outside the JSON.

Required schema:

{{
    "probable_cause": "string",
    "affected_segment": "string",
    "recommended_action": "string",
    "severity": "LOW|MEDIUM|HIGH|CRITICAL",
    "confidence": 0.0,
    "source_evidence": ["string"]
}}

CASE EVIDENCE

Representative Complaint:
{context["case"]["representative_text"]}

Topic:
{context["topic"]["topic_name"]}

Department:
{context["topic"]["department"]}

Sentiment:
{context["sentiment"]["sentiment"]}

Sentiment Confidence:
{context["sentiment"]["confidence"]}

Complaints In Latest 6-Hour Window:
{context["spike"]["current"]}

Normal Rate Per 6-Hour Window (last 7 days):
{context["spike"].get("baseline_rate", "unknown")}

Spike Detected:
{"yes (critical)" if context["spike"].get("critical") else "yes" if context["spike"].get("spike") else "no"}

Recent Complaints:
{complaint_text}
""".strip()


def _normalize_confidence(value):
    if isinstance(value, (int, float)):
        return max(
            0.0,
            min(1.0, float(value))
        )

    if isinstance(value, str):
        value = value.strip().lower()

        mapping = {
            "low": 0.35,
            "medium": 0.60,
            "moderate": 0.60,
            "high": 0.80,
            "very high": 0.90,
        }

        if value in mapping:
            return mapping[value]

        try:
            numeric = float(value)

            if numeric > 1:
                numeric = numeric / 100

            return max(
                0.0,
                min(1.0, numeric)
            )

        except ValueError:
            pass

    return 0.50


def _normalize_severity(value):
    severity = str(
        value or "MEDIUM"
    ).strip().upper()

    allowed = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    if severity not in allowed:
        return "MEDIUM"

    return severity


def _normalize_evidence(value):
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item)
            for item in value
        ][:5]

    return [str(value)]


def generate_rca(
    case_id,
    force_regenerate=False,
    save_result=True,
):
    # Keep existing cache behaviour by default.
    existing = get_rca(
        case_id
    )

    if existing and not force_regenerate:
        return existing

    context = fetch_rca_context(
        case_id
    )

    prompt = build_prompt(
        context
    )

    data = generate_json(
        prompt
    )

    required_fields = [
        "probable_cause",
        "affected_segment",
        "recommended_action",
    ]

    missing = [
        field
        for field in required_fields
        if not data.get(field)
    ]

    if missing:
        raise RuntimeError(
            "LLM response missing required "
            f"fields: {missing}"
        )

    rca = RCAResult(
        probable_cause=str(
            data["probable_cause"]
        ),

        affected_segment=str(
            data["affected_segment"]
        ),

        recommended_action=str(
            data["recommended_action"]
        ),

        severity=_normalize_severity(
            data.get("severity")
        ),

        confidence=_normalize_confidence(
            data.get("confidence")
        ),

        source_evidence=_normalize_evidence(
            data.get("source_evidence")
        ),

        generated_at=datetime.now(
            timezone.utc
        ).isoformat(),

        model_used=(
            f"{get_provider()}:"
            f"{get_model_name()}"
        ),
    )
    if save_result:
            save_rca(
              case_id,
              rca
            )

    return rca


if __name__ == "__main__":
    print(
        "Provider:",
        get_provider()
    )

    print(
        "Model:",
        get_model_name()
    )

    result = generate_rca(
        71,
        force_regenerate=True,
    )

    print(result)