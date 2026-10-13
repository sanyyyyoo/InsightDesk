from datetime import datetime, timezone
from collections import Counter
from backend.services.email_service import (
    escalate_case,
)
from fastapi import APIRouter, HTTPException
from backend.database.supabase import (
    get_clustering_statistics,
    get_clustering_metadata,
)
from backend.database.supabase import (
    get_cases,
    get_case,
    get_complaints,
    get_complaints_by_case,
    get_topics,
    get_benchmarks,
    get_rca,
    get_complaint_volume_by_day,
    get_case_history_bulk,
)

from backend.services.spike_detection import (
    detect_spike,
    detect_spikes_bulk,
    detect_group_from_history,
)
from backend.services.alert_groups import build_groups
from backend.services.escalation_policy import escalation_check
from backend.services import unassigned_spikes


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


# ==========================================
# OVERVIEW
# ==========================================

@router.get("/overview")
def get_dashboard_overview():

    try:

        # ----------------------------------
        # BASIC PROJECT DATA
        # ----------------------------------

        cases = get_cases()

        complaints = get_complaints()

        topics = get_topics()

        benchmarks = get_benchmarks()


        # ----------------------------------
        # COMPLAINT VOLUME BY DAY
        # ----------------------------------

        raw_volume = get_complaint_volume_by_day()

        daily_counts = Counter()

        for row in raw_volume:

            created_at = row.get("created_at")

            if not created_at:
                continue

            # Supabase timestamps may contain
            # variable fractional-second precision.
            #
            # We only need the calendar date,
            # so extracting the first 10 characters
            # is safer than datetime.fromisoformat().

            date = created_at[:10]

            daily_counts[date] += 1


        volume_by_day = [

            {
                "date": date,

                "label":
                date[5:7] + "/" + date[8:10],

                "count":
                daily_counts[date],
            }

            for date in sorted(daily_counts)
        ]


        # ----------------------------------
        # SPIKE DETECTION
        # ----------------------------------

        case_ids = [
            case["case_id"]
            for case in cases
        ]

        raw_history = get_case_history_bulk(
            case_ids
        )

        history_by_case = {}

        for row in raw_history:

            case_id = row["case_id"]

            if case_id not in history_by_case:

                history_by_case[case_id] = []

            history_by_case[case_id].append(
                row
            )


        spike_results = detect_spikes_bulk(
            cases,
            history_by_case
        )


        spike_cases = []

        for case in cases:

            case_id = case["case_id"]

            result = spike_results.get(
                case_id,
                {
                    "spike": False,
                    "critical": False,
                    "z_score": 0,
                    "current": 0,
                }
            )

            if result["spike"]:

                spike_cases.append(

                    {
                        "case_id":
                        case_id,

                        "representative_text":
                        case.get(
                            "representative_text"
                        ),

                        **result,
                    }

                )


        # ----------------------------------
        # OVERVIEW RESPONSE
        # ----------------------------------

        return {

            "complaints":
            len(complaints),

            "cases":
            len(cases),

            "topics":
            len(topics),

            "spikes":
            len(spike_cases),

            "spike_cases":
            spike_cases,

            "benchmarks":
            benchmarks,

            "topics_data":
            topics,

            "volume_by_day":
            volume_by_day,
        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )


# ==========================================
# CASES
# ==========================================

@router.get("/cases")
def dashboard_cases():

    try:

        return get_cases()

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )

# ==========================================
# CASE INTELLIGENCE
# ==========================================

@router.get("/cases/{case_id}/intelligence")
def dashboard_case_intelligence(
    case_id: int
):

    try:

        # ----------------------------------
        # CASE
        # ----------------------------------

        case = get_case(case_id)

        if not case:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found."
            )

        # ----------------------------------
        # COMPLAINTS
        # ----------------------------------

        complaints = get_complaints_by_case(
            case_id
        )

        # ----------------------------------
        # TOPIC + DEPARTMENT
        # ----------------------------------

        topic = None

        topic_id = case.get("topic_id")

        if topic_id is not None:

            topics = get_topics()

            topic = next(
                (
                    item
                    for item in topics
                    if item.get("topic_id") == topic_id
                ),
                None,
            )

        # ----------------------------------
        # CURRENT SPIKE ANALYSIS
        # ----------------------------------

        spike = detect_spike(
            case_id
        )

        # ----------------------------------
        # EXISTING RCA
        # ----------------------------------

        rca = get_rca(
            case_id
        )

        # ----------------------------------
        # RESPONSE
        # ----------------------------------

        in_group_spike = any(
            case_id in g["case_ids"] for g in compute_group_spikes()
        )

        escalation = escalation_check(case, spike, in_group_spike)

        return {
            "case": case,
            "complaints": complaints,
            "topic": topic,
            "spike": spike,
            "rca": rca,
            "in_group_spike": in_group_spike,
            "escalation": escalation,
            "rca_recommended": escalation["eligible"],
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
# ==========================================
# COMPLAINTS
# ==========================================

@router.get("/complaints")
def dashboard_complaints():

    try:

        return get_complaints()

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )


# ==========================================
# TOPICS
# ==========================================

@router.get("/topics")
def dashboard_topics():

    try:

        return get_topics()

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )

# ==========================================
# CLUSTERS
# ==========================================

@router.get("/clusters")
def dashboard_clusters():

    try:

        topics = get_topics()
        cases = get_cases()

        statistics = get_clustering_statistics()
        metadata = get_clustering_metadata()

        # ----------------------------------
        # GROUP CASES BY TOPIC
        # ----------------------------------

        cases_by_topic = {}

        for case in cases:

            topic_id = case.get("topic_id")

            if topic_id is None:
                continue

            cases_by_topic.setdefault(
                topic_id,
                []
            ).append(case)

        # ----------------------------------
        # BUILD TOPIC DATA
        # ----------------------------------

        topic_data = []

        for topic in topics:

            topic_id = topic.get("topic_id")

            assigned_cases = cases_by_topic.get(
                topic_id,
                []
            )

            representative_cases = []

            for case in assigned_cases[:5]:

                representative_cases.append(
                    {
                        "case_id": case.get("case_id"),
                        "representative_text":
                            case.get("representative_text"),
                        "sentiment":
                            case.get("sentiment"),
                        "report_count":
                            case.get("report_count"),
                    }
                )

            topic_data.append(
                {
                    "topic_id": topic_id,
                    "topic_name":
                        topic.get("topic_name"),
                    "department":
                        topic.get("department"),
                    "description":
                        topic.get("description"),
                    "case_count":
                        len(assigned_cases),
                    "representative_cases":
                        representative_cases,
                }
            )

        # Most populated topics first
        topic_data.sort(
            key=lambda topic: topic["case_count"],
            reverse=True,
        )

        # ----------------------------------
        # RESPONSE
        # ----------------------------------

        return {
            "case_count":
                statistics.get("case_count", 0),

            "topic_count":
                len(topics),

            "outlier_count":
                statistics.get("outlier_count", 0),

            "outlier_rate":
                statistics.get("outlier_rate", 0),

            "clustering_version":
                metadata.get("clustering_version", 0),

            "last_clustered_at":
                metadata.get("last_clustered_at"),

            "topics":
                topic_data,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
# ==========================================
# BENCHMARKS
# ==========================================

@router.get("/benchmarks")
def dashboard_benchmarks():

    try:

        return get_benchmarks()

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )


# ==========================================
# SPIKES
# ==========================================

@router.get("/spikes")
def dashboard_spikes():

    try:

        cases = get_cases()

        spikes = []

        for case in cases:

            result = detect_spike(
                case["case_id"]
            )

            if result["spike"]:

                spikes.append(

                    {
                        "case_id":
                        case["case_id"],

                        "representative_text":
                        case.get(
                            "representative_text"
                        ),

                        **result,
                    }

                )

        return spikes


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )


# ==========================================
# GROUP SPIKES (related cases counted together)
# ==========================================

def compute_group_spikes():
    """Alert-group spikes (see /group-spikes); also used by case intelligence and escalation."""

    cases = {c["case_id"]: c for c in get_cases()}

    group_of = build_groups(get_complaints())

    members = {}
    for case_id, group_id in group_of.items():
        members.setdefault(group_id, []).append(case_id)

    multi = {g: sorted(m) for g, m in members.items() if len(m) >= 2}

    history = get_case_history_bulk(
        [c for m in multi.values() for c in m]
    ) if multi else []

    rows_by_case = {}
    for row in history:
        rows_by_case.setdefault(row["case_id"], []).append(row)

    spikes = []

    for group_id, case_ids in multi.items():

        rows = [r for c in case_ids for r in rows_by_case.get(c, [])]

        result = detect_group_from_history(rows)

        if result["spike"]:

            spikes.append(
                {
                    "group_id": group_id,
                    "case_ids": case_ids,
                    "representative_texts": [
                        cases.get(c, {}).get("representative_text")
                        for c in case_ids
                    ],
                    **result,
                }
            )

    return spikes


@router.get("/vague-summary")
def dashboard_vague_summary():
    """
    Complaints the dedup judge found too vague to group ("app is useless"):
    each is its own case, kept out of RCA and escalation, and counted here
    per product as a general-dissatisfaction signal.
    """

    try:

        vague = [c for c in get_cases() if c.get("is_vague")]

        product_of = {}
        for row in get_complaints():
            if row.get("case_id") is not None:
                product_of.setdefault(row["case_id"], row.get("product") or "unknown")

        cases_by = Counter()
        complaints_by = Counter()
        for c in vague:
            p = product_of.get(c["case_id"], "unknown")
            cases_by[p] += 1
            complaints_by[p] += int(c.get("report_count") or 1)

        return {
            "vague_cases": len(vague),
            "vague_complaints": sum(complaints_by.values()),
            "by_product": [
                {"product": p, "cases": cases_by[p], "complaints": complaints_by[p]}
                for p in sorted(cases_by, key=lambda k: -complaints_by[k])
            ],
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


def _history_chunked(case_ids):
    rows = []
    for k in range(0, len(case_ids), unassigned_spikes.CHUNK):
        rows += get_case_history_bulk(case_ids[k:k + unassigned_spikes.CHUNK])
    return rows


@router.get("/unassigned-spikes")
def dashboard_unassigned_spikes():
    """
    Outage signal (separate from dedup): per product, complaints the judge could not place in a
    specific case (cases.is_vague), counted per 6-hour window with spike detector v2. An alert
    means "possible outage or widespread degradation", shown with the product's specific cases
    active in the same window. Off unless UNASSIGNED_SPIKES=1. See services/unassigned_spikes.py.
    """

    if not unassigned_spikes.enabled():
        return {"enabled": False, "products": []}

    try:

        cases = {c["case_id"]: c for c in get_cases()}

        product_of_case = {}
        for row in get_complaints():
            if row.get("case_id") is not None:
                product_of_case.setdefault(row["case_id"], row.get("product") or "unknown")

        vague_by_product = {}
        for case_id, case in cases.items():
            if case.get("is_vague"):
                vague_by_product.setdefault(product_of_case.get(case_id, "unknown"), []).append(case_id)

        results = unassigned_spikes.detect(
            vague_by_product,
            _history_chunked([c for ids in vague_by_product.values() for c in ids]),
            now=datetime.now(timezone.utc),
        )

        for r in results:
            if r["spike"]:
                specific = [c for c, p in product_of_case.items()
                            if p == r["product"] and not cases.get(c, {}).get("is_vague")]
                r["related_cases"] = unassigned_spikes.related_cases(
                    r["product"], r["window_start"], cases, product_of_case, _history_chunked(specific))

        return {"enabled": True, "products": results}

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/rejoin")
def dashboard_rejoin():
    """
    One case re-joining pass (services/rejoin.py): merges cases that report the same problem,
    as judged by the LLM on up to 3 complaints per case. Off unless REJOIN_ENABLED=1.
    Run it periodically (e.g. hourly); each pass merges a case at most once.
    """

    from backend.services import rejoin

    if not rejoin.enabled():
        return {"enabled": False, "merges": []}

    try:

        import backend.database.supabase as db
        from backend.services.embedding_service import model

        merges = rejoin.run_pass(
            db, lambda texts: model.encode(texts, normalize_embeddings=True, show_progress_bar=False))
        return {"enabled": True, "merges": [{"kept": int(k), "absorbed": int(a)} for k, a in merges]}

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/group-spikes")
def dashboard_group_spikes():
    """
    Spikes of alert groups: related cases of one product counted together
    (cases themselves are unchanged; RCA stays per case). Only groups that
    join two or more cases are checked; each alert lists its cases.
    """

    try:

        return compute_group_spikes()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================
# RCA
# ==========================================

@router.get("/rca/{case_id}")
def dashboard_rca(
    case_id: int
):

    try:

        rca = get_rca(
            case_id
        )

        if not rca:

            raise HTTPException(

                status_code=404,

                detail=(
                    f"No RCA found "
                    f"for case {case_id}"
                ),
            )

        return rca


    except HTTPException:

        raise


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e),
        )
# ==========================================
# EMAIL ESCALATION
# ==========================================

@router.post("/cases/{case_id}/escalate")
def dashboard_escalate_case(
    case_id: int,
    force: bool = False,
):
    try:
        case = get_case(case_id)

        if not case:
            raise HTTPException(
                status_code=404,
                detail=f"Case {case_id} not found.",
            )

        policy = escalation_check(
            case,
            detect_spike(case_id),
            any(case_id in g["case_ids"] for g in compute_group_spikes()),
        )

        if not policy["eligible"] and not force:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Case does not meet the escalation policy. "
                               "Use force=true to escalate anyway.",
                    **policy,
                },
            )

        success = escalate_case(case_id)

        if not success:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Case could not be escalated. "
                    "Check RCA availability, severity, "
                    "department mapping, and email configuration."
                ),
            )

        return {
            "status": "success",
            "case_id": case_id,
            "message": f"Case #{case_id} escalated successfully.",
            "forced": bool(force and not policy["eligible"]),
            "policy": policy,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )