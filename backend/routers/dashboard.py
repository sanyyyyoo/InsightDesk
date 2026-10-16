import logging
from collections import Counter
from dataclasses import asdict, is_dataclass

from backend.services.email_service import (
    escalate_case,
)
from fastapi import APIRouter, Depends, HTTPException
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
    get_case_original_texts,
)

from backend.services.spike_detection import (
    detect_spike,
    detect_spikes_bulk,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

logger = logging.getLogger(__name__)


def get_rca_generator():
    """
    The RCA generator, imported lazily (it loads the LLM client).
    Overridable in tests.
    """
    from backend.services.rca_service import generate_rca

    return generate_rca


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

        return {
            "case": case,
            "complaints": complaints,
            "topic": topic,
            "spike": spike,
            "rca": rca,
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


@router.get("/case-texts")
def dashboard_case_texts():
    """Readable title per case: the original text of its first complaint."""

    try:

        return {str(k): v for k, v in get_case_original_texts().items()}

    except Exception:

        logger.exception("Reading case texts failed")

        raise HTTPException(status_code=500, detail="Could not read case texts.")


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
# RCA GENERATION (on demand only)
# ==========================================

@router.post("/cases/{case_id}/rca")
def dashboard_generate_rca(
    case_id: int,
    force: bool = False,
    generate=Depends(get_rca_generator),
):
    """
    Generate an RCA for one case when an operator asks for it.

    RCAs are never produced automatically. Without force=true an
    existing RCA is returned unchanged; force=true regenerates it
    (new LLM call, new row in case_rca).
    """

    if not get_case(case_id):
        raise HTTPException(
            status_code=404,
            detail=f"Case {case_id} not found.",
        )

    try:
        result = generate(
            case_id,
            force_regenerate=force,
        )

    except RuntimeError as e:
        # rca_service raises RuntimeError when the LLM output is unusable
        logger.warning("RCA generation failed for case %s: %s", case_id, e)
        raise HTTPException(
            status_code=502,
            detail="The LLM did not return a usable RCA. Please try again.",
        )

    except Exception:
        logger.exception("RCA generation failed for case %s", case_id)
        raise HTTPException(
            status_code=500,
            detail="RCA generation failed. Check the LLM provider configuration.",
        )

    return asdict(result) if is_dataclass(result) else result


# ==========================================
# EMAIL ESCALATION
# ==========================================

@router.post("/cases/{case_id}/escalate")
def dashboard_escalate_case(
    case_id: int
):
    try:
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
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )