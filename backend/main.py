from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ai.ranker import rank_matches
from ai.classifier import classify_intent
from ai.extractor import extract_attributes
from ai.explainer import generate_action_plan
from ai.ranker import rank_matches


# Adjust this import to match your repo layout.
# If traversal.py lives in backend/graph/traversal.py, this should work when run from backend.
from graph.traversal import traverse_programs
from schemas import (
    IntakeProfile,
    IntakeResponse,
    Program,
    ProgramMatch,
    RoutingResult,
    SessionRecord,
    ClassifiedIntent,
    ActionStep,
)

# =============================
# App setup
# =============================


app = FastAPI(title="PathForward API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, SessionRecord] = {}
PROGRAMS: List[Program] = []


@app.on_event("startup")
def load_program_data() -> None:
    """Load seeded JSON programs into memory at startup."""
    global PROGRAMS

    programs_dir = Path("data/programs")
    loaded: List[Program] = []

    if programs_dir.exists():
        for path in sorted(programs_dir.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(raw, list):
                    loaded.extend(Program.model_validate(item) for item in raw)
                else:
                    loaded.append(Program.model_validate(raw))
            except Exception as exc:  # pragma: no cover - startup guard
                print(f"Skipping {path}: {exc}")

    PROGRAMS = loaded
    print(f"Loaded {len(PROGRAMS)} programs")


# =============================
# Helpers
# =============================


def classify_intent(profile: IntakeProfile) -> ClassifiedIntent:
    """Simple deterministic placeholder until you wire Claude in."""
    text = f"{profile.free_text} {' '.join(profile.urgent_needs)}".lower()

    if any(word in text for word in ["equipment", "mixer", "broken", "repair"]):
        return ClassifiedIntent(
            primary_intent="equipment_emergency",
            urgency_level="this_week",
            extracted_facts={"asset_type": "equipment"},
            confidence=0.88,
        )

    if any(word in text for word in ["cashflow", "cash flow", "reimbursement", "bill", "bills"]):
        return ClassifiedIntent(
            primary_intent="cashflow_gap",
            urgency_level="immediate",
            extracted_facts={"financial_issue": "cashflow"},
            confidence=0.84,
        )

    if any(word in text for word in ["rent", "eviction", "housing", "shelter"]):
        return ClassifiedIntent(
            primary_intent="housing_need",
            urgency_level="immediate",
            extracted_facts={"need": "housing"},
            confidence=0.82,
        )

    return ClassifiedIntent(
        primary_intent="general_assistance",
        urgency_level="this_month",
        extracted_facts={},
        confidence=0.55,
    )


def build_action_plan(
    profile: IntakeProfile,
    intent: ClassifiedIntent,
    ranked_matches: List[ProgramMatch],
) -> List[ActionStep]:
    """Deterministic starter action plan for hackathon MVP."""
    steps: List[ActionStep] = []

    if ranked_matches:
        top = ranked_matches[0]
        steps.append(
            ActionStep(
                description=f"Review {top.name} from {top.org_name} and gather the required documents.",
                program_id=top.program_id,
                is_parallel=False,
            )
        )

        if top.documents_needed:
            docs = ", ".join(top.documents_needed)
            steps.append(
                ActionStep(
                    description=f"Prepare documents: {docs}.",
                    program_id=top.program_id,
                    is_parallel=True,
                )
            )

    if intent.primary_intent == "equipment_emergency":
        steps.append(
            ActionStep(
                description="Take a photo or invoice screenshot of the broken equipment so you can prove the need.",
                is_parallel=True,
            )
        )
    elif intent.primary_intent == "cashflow_gap":
        steps.append(
            ActionStep(
                description="Collect the most recent bill, invoice, or reimbursement notice to show the timing gap.",
                is_parallel=True,
            )
        )
    elif intent.primary_intent == "housing_need":
        steps.append(
            ActionStep(
                description="Save lease, eviction, or shelter-related paperwork before applying.",
                is_parallel=True,
            )
        )

    return steps


def build_routing_result(session_id: str, profile: IntakeProfile) -> RoutingResult:
    """Run the pure-Python matching pipeline end-to-end."""
    intent = classify_intent(profile)
    extracted = extract_attributes(profile.free_text)
    profile.extracted_attributes.update(extracted)
    
    raw_matches = traverse_programs(profile, PROGRAMS)
    ranked_matches = rank_matches(raw_matches, intent, top_k=15)

    action_plan = build_action_plan(profile, intent, ranked_matches[:3])

    fairness_flags: List[str] = []
    if profile.location.county and profile.location.county.lower() != "los angeles":
        fairness_flags.append("Profile is outside the LA County demo scope")

    return RoutingResult(
        session_id=session_id,
        classified_intent=intent,
        ranked_matches=ranked_matches,
        action_plan=action_plan,
        fairness_flags=fairness_flags,
    )


def process_session(session_id: str, profile: IntakeProfile) -> None:
    """Background task that evaluates the profile and stores the result."""
    try:
        result = build_routing_result(session_id, profile)
        SESSIONS[session_id] = SessionRecord(status="complete", result=result)
    except Exception as exc:  # pragma: no cover - runtime safety
        SESSIONS[session_id] = SessionRecord(status="error", error=str(exc))


# =============================
# Routes
# =============================


@app.get("/health")
def health() -> Dict[str, Any]:
    """Basic service health check."""
    return {
        "status": "ok",
        "graph_loaded": len(PROGRAMS) > 0,
        "program_count": len(PROGRAMS),
    }


@app.post("/api/intake", response_model=IntakeResponse)
def intake(profile: IntakeProfile, background_tasks: BackgroundTasks) -> IntakeResponse:
    """Accept intake data and start routing in the background."""
    session_id = profile.session_id or str(uuid4())
    profile.session_id = session_id

    SESSIONS[session_id] = SessionRecord(status="processing")
    background_tasks.add_task(process_session, session_id, profile)

    return IntakeResponse(session_id=session_id, status="processing")


@app.get("/api/results/{session_id}", response_model=RoutingResult)
def get_results(session_id: str) -> RoutingResult:
    """Fetch completed routing results for a given session."""
    record = SESSIONS.get(session_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if record.status == "error":
        raise HTTPException(status_code=500, detail=record.error or "Processing failed")

    if record.status != "complete" or record.result is None:
        raise HTTPException(status_code=202, detail="Results are still processing")

    return record.result


# Optional local entrypoint:
# uvicorn backend_main:app --reload --port 8000
