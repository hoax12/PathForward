# backend/graph/traversal.py

from __future__ import annotations

from typing import Any, Iterable, List, Tuple

from schemas import IntakeProfile, Program, ProgramMatch


SPEED_ORDER = {
    "same_day": 0,
    "1-3_days": 1,
    "1-2_weeks": 2,
    "varies": 3,
}

MUST_WEIGHT = 2.0
PREFERRED_WEIGHT = 1.0


def traverse_programs(
    profile: IntakeProfile,
    programs: Iterable[Program],
) -> List[ProgramMatch]:
    """
    Evaluate a profile against a set of programs and return ranked matches.

    This is pure Python:
    - no LLM calls
    - no API calls
    - no graph database dependency

    The function evaluates each criterion, computes an eligibility score,
    and returns ProgramMatch objects sorted by:
    1) whether all must criteria are met
    2) eligibility score
    3) speed_to_fund
    4) max_amount
    """
    matches: List[ProgramMatch] = []

    for program in programs:
        match = score_program(profile, program)
        matches.append(match)

    return matches


def score_program(profile: IntakeProfile, program: Program) -> ProgramMatch:
    """
    Score a single program against a user profile.

    Scoring rule:
    - must criteria count double
    - preferred criteria count single
    - score = matched_weight / total_weight

    The returned ProgramMatch includes explainability fields:
    - eligibility_criteria_met
    - eligibility_criteria_missing
    """
    met: List[str] = []
    missing: List[str] = []

    total_weight = 0.0
    matched_weight = 0.0

    for criterion in program.eligibility_criteria:
        weight = MUST_WEIGHT if criterion.type == "must" else PREFERRED_WEIGHT
        total_weight += weight

        passed = evaluate_criterion(profile, criterion.field, criterion.operator, criterion.value)

        if passed:
            met.append(criterion.id)
            matched_weight += weight
        else:
            missing.append(criterion.id)

    eligibility_score = 1.0 if total_weight == 0 else round(matched_weight / total_weight, 4)

    return ProgramMatch(
        program_id=program.program_id,
        name=program.name,
        org_name=program.org_name,
        eligibility_score=eligibility_score,
        eligibility_criteria_met=met,
        eligibility_criteria_missing=missing,
        speed_to_fund=program.speed_to_fund,
        max_amount=program.max_amount,
        program_type=program.program_type,
        documents_needed=program.documents_needed,
        application_url=program.application_url,
        data_verified_date=program.data_verified_date,
    )


def evaluate_criterion(
    profile: IntakeProfile,
    field: str,
    operator: str,
    value: Any,
) -> bool:
    """
    Evaluate a single criterion against the intake profile.

    Supports nested fields like:
    - location.county
    - location.city
    - extracted_attributes.asset_type
    - urgent_needs
    """
    actual = _get_field_value(profile, field)

    if operator == "exists":
        return _exists(actual)

    if operator == "equals":
        return _equals(actual, value)

    if operator == "in":
        return _in(actual, value)

    if operator == "contains":
        return _contains(actual, value)

    if operator == "gte":
        return _compare_numeric(actual, value, ">=")

    if operator == "lte":
        return _compare_numeric(actual, value, "<=")

    raise ValueError(f"Unsupported operator: {operator}")


def _all_must_criteria_met(profile: IntakeProfile, program: Program) -> bool:
    """Return True only if every 'must' criterion is satisfied."""
    for criterion in program.eligibility_criteria:
        if criterion.type == "must":
            if not evaluate_criterion(profile, criterion.field, criterion.operator, criterion.value):
                return False
    return True


def _get_field_value(profile: IntakeProfile, field_path: str) -> Any:
    """
    Resolve dot-path access against the profile object.

    Examples:
    - location.county
    - location.zip_code
    - extracted_attributes.asset_type
    - urgent_needs
    """
    current: Any = profile

    for part in field_path.split("."):
        if current is None:
            return None

        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)

    return current


def _exists(actual: Any) -> bool:
    if actual is None:
        return False
    if isinstance(actual, str):
        return actual.strip() != ""
    if isinstance(actual, (list, tuple, set, dict)):
        return len(actual) > 0
    return True


def _equals(actual: Any, expected: Any) -> bool:
    if isinstance(actual, str) and isinstance(expected, str):
        return actual.strip().lower() == expected.strip().lower()
    return actual == expected


def _in(actual: Any, expected: Any) -> bool:
    if expected is None:
        return False

    if isinstance(expected, (list, tuple, set)):
        if isinstance(actual, (list, tuple, set)):
            return any(item in expected for item in actual)
        return actual in expected

    return actual == expected


def _contains(actual: Any, expected: Any) -> bool:
    if actual is None:
        return False

    if isinstance(actual, str) and isinstance(expected, str):
        return expected.strip().lower() in actual.lower()

    if isinstance(actual, (list, tuple, set)):
        if isinstance(expected, str):
            return any(
                isinstance(item, str) and item.strip().lower() == expected.strip().lower()
                for item in actual
            )
        return expected in actual

    return False


def _compare_numeric(actual: Any, expected: Any, op: str) -> bool:
    try:
        actual_num = float(actual)
        expected_num = float(expected)
    except (TypeError, ValueError):
        return False

    if op == ">=":
        return actual_num >= expected_num
    if op == "<=":
        return actual_num <= expected_num

    raise ValueError(f"Unsupported numeric operator: {op}")