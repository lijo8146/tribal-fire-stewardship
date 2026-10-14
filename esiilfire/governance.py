"""Explicit decisions, never inferred permission or numeric Nation rankings."""
REQUIRED_DECISIONS = ("lead_authority", "research_question", "study_area_authority", "benefit_and_compensation", "data_steward", "access_rules", "interpretation_review", "release_authority", "withdrawal_and_retention")
def decision_gaps(plan):
    return [key for key in REQUIRED_DECISIONS if not isinstance(plan.get(key), str) or not plan[key].strip()]
def review_public_release(record):
    required = ("asset", "owner", "purpose", "audience", "approved_by", "approved_on", "approval_reference")
    missing = [key for key in required if not isinstance(record.get(key), str) or not record[key].strip()]
    if record.get("classification") != "public" or record.get("decision") != "approved":
        missing.append("explicit public approval")
    return {"release_allowed": not missing, "missing": missing}
