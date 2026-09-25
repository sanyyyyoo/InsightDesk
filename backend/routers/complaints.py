import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth import AuthUser, get_current_user
from backend.models.complaint import ComplaintCreate, ComplaintSubmit
from backend.services.preprocess import clean_text


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Complaints"],
)

# A complaint must keep at least this many words after cleaning
# (stop words removed), otherwise it carries too little meaning to
# embed and match against existing cases.
MIN_CLEANED_WORDS = 2

WEB_PORTAL_SOURCE = "web_portal"


def get_pipeline():
    """
    The complaint pipeline, imported lazily so the ML models load on
    first use. Overridable in tests.
    """
    from backend.services.duplicate_service import process_complaint

    return process_complaint


@router.post("/analyze")
def analyze_complaint(
    submission: ComplaintSubmit,
    user: AuthUser = Depends(get_current_user),
    process_complaint=Depends(get_pipeline),
):
    """
    Submit a complaint as the logged-in customer.

    user_id comes only from the verified token; it is stored as
    complaint metadata and does not affect embeddings, retrieval,
    reranking, the duplicate threshold, sentiment or clustering.
    """

    if len(clean_text(submission.complaint_text).split()) < MIN_CLEANED_WORDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Please describe the problem in a bit more detail "
                "(what happened, and where)."
            ),
        )

    complaint = ComplaintCreate(
        complaint_text=submission.complaint_text.strip(),
        user_id=user.id,
        rating=submission.rating,
        source=WEB_PORTAL_SOURCE,
        product=submission.product,
    )

    try:

        return process_complaint(
            complaint
        )

    except Exception:

        logger.exception(
            "Complaint pipeline failed for user %s", user.id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="We couldn't process your complaint. Please try again.",
        )
