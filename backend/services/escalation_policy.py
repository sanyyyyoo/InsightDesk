"""
When a case is worth an RCA and an escalation email.

A wrong email to a department is the costliest mistake the system can make,
and single-complaint cases rarely need a root-cause analysis. A case qualifies
when it is NOT vague and it has at least ESCALATION_MIN_REPORTS reports or is
part of an active spike (case alert or alert-group alert). A human can still
escalate anything with force=True; the response records that it was forced.
"""

import os

MIN_REPORTS = int(os.getenv("ESCALATION_MIN_REPORTS", "3"))


def escalation_check(case, spike=None, in_group_spike=False):
    """Returns {"eligible": bool, "reasons": [...]} for a case row."""
    reasons = []
    if case.get("is_vague"):
        reasons.append("vague complaint (no concrete symptom); counted in the vague summary instead")
    reports = int(case.get("report_count") or 0)
    spiking = bool(spike and spike.get("spike")) or bool(in_group_spike)
    if reports < MIN_REPORTS and not spiking:
        reasons.append(f"only {reports} report(s) and no active spike (needs >= {MIN_REPORTS} or a spike)")
    return {"eligible": not reasons, "reasons": reasons, "reports": reports, "spiking": spiking,
            "min_reports": MIN_REPORTS}


def rca_recommended(case, spike=None, in_group_spike=False):
    """Same bar as escalation: RCA is generated where it can lead to action."""
    return escalation_check(case, spike, in_group_spike)["eligible"]
