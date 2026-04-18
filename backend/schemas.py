from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# =============================
# Pydantic models
# =============================


class Location(BaseModel):
    zip_code: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None


class EligibilityCriterion(BaseModel):
    id: str
    type: Literal["must", "preferred"]
    field: str
    operator: Literal["equals", "in", "contains", "gte", "lte", "exists"]
    value: Any
    description: str





class ClassifiedIntent(BaseModel):
    primary_intent: str
    urgency_level: Literal["immediate", "this_week", "this_month"]
    extracted_facts: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)





class ActionStep(BaseModel):
    description: str
    program_id: Optional[str] = None
    is_parallel: bool = False
    deadline_note: Optional[str] = None


class RoutingResult(BaseModel):
    session_id: str
    classified_intent: ClassifiedIntent
    ranked_matches: List[ProgramMatch]
    action_plan: List[ActionStep] = Field(default_factory=list)
    fairness_flags: List[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class IntakeResponse(BaseModel):
    session_id: str
    status: Literal["processing"]


class SessionRecord(BaseModel):
    status: Literal["processing", "complete", "error"] = "processing"
    result: Optional[RoutingResult] = None
    error: Optional[str] = None


class Program(BaseModel):
    program_id: str
    name: str
    org_id: str
    org_name: str
    program_type: Literal["grant", "microloan", "fee_free_product", "referral"]
    description: str
    max_amount: Optional[int] = None
    speed_to_fund: Literal["same_day", "1-3_days", "1-2_weeks", "varies"]
    eligibility_criteria: List[EligibilityCriterion]
    documents_needed: List[str] = Field(default_factory=list)
    application_url: str
    source_url: Optional[str] = None
    data_verified_date: str


class IntakeProfile(BaseModel):
    session_id: Optional[str] = None
    location: Location = Field(default_factory=Location)
    income_band: Literal["0-20k", "20-35k", "35-50k", "50-75k", "75k+"]
    employment_status: Literal["self_employed", "1099_contractor", "employee", "unemployed"]
    business_type: Optional[Literal["food", "retail", "services", "healthcare", "childcare", "other"]] = None
    urgent_needs: List[str] = Field(default_factory=list)
    free_text: str
    monthly_revenue: Optional[int] = None
    has_paypal_account: bool = False
    extracted_attributes: Dict[str, Any] = Field(default_factory=dict)
    
class ProgramMatch(BaseModel):
    program_id: str
    name: str
    org_name: str
    eligibility_score: float = Field(..., ge=0.0, le=1.0)
    eligibility_criteria_met: List[str] = Field(default_factory=list)
    eligibility_criteria_missing: List[str] = Field(default_factory=list)
    speed_to_fund: Literal["same_day", "1-3_days", "1-2_weeks", "varies"]
    max_amount: Optional[int] = None
    program_type: Literal["grant", "microloan", "fee_free_product", "referral"]
    documents_needed: List[str] = Field(default_factory=list)
    application_url: Optional[str] = None
    data_verified_date: str