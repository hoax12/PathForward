# PathForward — CLAUDE.md

This file lives at the repo root and is read by Claude Code / Cursor sessions for project context.

## Project Summary

PathForward is an AI-powered financial benefits routing system for underbanked individuals and micro-businesses in Los Angeles County.

It is **not a chatbot** and **not a general financial advisor**.
It is a decision-support and routing engine that takes structured intake data, evaluates eligibility against a program graph, and returns ranked, explainable recommendations plus a step-by-step action plan.

Hackathon target: PayPal AI for Social Good 48-hour build.
Demo scope: Los Angeles County only.
Core value prop: 90-second intake → ranked list of real or demo-grounded programs → clear action plan.

## Current Project Status

Backend, graph traversal, ranking, and AI orchestration are already implemented.
The remaining major surface area is the frontend.

Use Claude Code primarily for **frontend work only** unless a backend change is explicitly requested.
Do not rewrite the backend architecture unless needed for a small, targeted fix.

## Operating Rule for Claude Code

Claude Code should be used to accelerate frontend implementation, styling, and polish.
Keep changes scoped and review diffs carefully.
Do not let Claude Code broadly refactor backend logic, model schemas, or ranking behavior unless you intentionally ask for that.

Recommended workflow:

* commit or checkpoint the current working backend state before making frontend changes
* work in a branch if possible
* keep edits scoped to frontend files unless asked otherwise
* preserve the current backend contracts

## Repository Structure

```text
pathforward/
├── CLAUDE.md
├── README.md
├── .env.example
│
├── backend/
│   ├── main.py
│   ├── schemas.py
│   ├── requirements.txt
│   │
│   ├── graph/
│   │   ├── builder.py
│   │   ├── schema.py
│   │   ├── traversal.py
│   │   └── loader.py
│   │
│   ├── ai/
│   │   ├── client.py
│   │   ├── classifier.py
│   │   ├── extractor.py
│   │   ├── ranker.py
│   │   ├── explainer.py
│   │   ├── fairness.py
│   │   └── prompts/
│   │       ├── classifier_v1.txt
│   │       ├── extractor_v1.txt
│   │       └── explainer_v1.txt
│   │
│   ├── data/
│   │   ├── programs/
│   │   └── graph_snapshot.json
│   │
│   ├── ingest/
│   │   ├── scrapers/
│   │   └── api_clients/
│   │
│   ├── api/
│   │   └── routes/
│   │
│   └── tests/
│       ├── test_traversal.py
│       ├── test_classifier.py
│       └── fixtures/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── IntakePage.tsx
│   │   │   └── ResultsPage.tsx
│   │   ├── components/
│   │   │   ├── IntakeForm/
│   │   │   ├── Results/
│   │   │   └── shared/
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── styles/
│   │       └── globals.css
│   └── public/
│
├── notebooks/
│   ├── 01_data_ingestion.ipynb
│   ├── 02_graph_builder.ipynb
│   ├── 03_embedding_index.ipynb
│   └── 04_evaluation.ipynb
│
└── scripts/
    ├── build_graph.py
    └── seed_demo_data.py
```

## Canonical Data Models

Always use the existing backend shapes. Do not invent new field names unless the change is deliberate and cross-cutting.

### IntakeProfile

Structured intake input from the frontend.

Typical fields:

* session_id
* location { zip_code, city, county }
* income_band
* employment_status
* business_type
* urgent_needs
* free_text
* monthly_revenue
* has_paypal_account
* extracted_attributes

### ClassifiedIntent

AI layer output.
Contains:

* primary_intent
* urgency_level
* extracted_facts
* confidence

### ProgramMatch

Graph traversal + ranking output.
Contains:

* program_id
* name
* org_name
* eligibility_score
* eligibility_criteria_met
* eligibility_criteria_missing
* speed_to_fund
* max_amount
* program_type
* documents_needed
* application_url
* data_verified_date

### RoutingResult

Full API response.
Contains:

* session_id
* classified_intent
* ranked_matches
* action_plan
* fairness_flags
* generated_at

### ActionStep

Action plan item.
Contains:

* description
* program_id
* is_parallel
* deadline_note

## Architecture Rules

### 1. Traversal and ranking are deterministic

Eligibility and ranking logic must remain pure Python.
Do not use the LLM to decide eligibility.
Do not use the LLM to rank programs.

### 2. LLMs are only for unstructured tasks

Use the LLM only for:

* intent classification from free text
* extracting hidden attributes from free text
* generating grounded action-plan steps

### 3. LLM outputs must be structured and grounded

The AI layer must return valid JSON that matches the backend schemas.
The explainer must only reference programs already present in the ranked match list.
Never allow the model to invent program names, URLs, amounts, or eligibility facts.

### 4. Keep files under 200 lines when practical

Split files if they become too large.
Prioritize readability and testability.

### 5. All API routes need docstrings

Keep backend routes explicit and easy to audit.

### 6. Use type hints everywhere in Python

Use Pydantic models for structured data.

### 7. Avoid hardcoding program data in code

Program names, URLs, amounts, and core eligibility rules belong in data files.

### 8. Mark mock/demo code clearly

Add `# TODO(demo):` comments wherever logic is synthetic or temporary.

## AI / LLM Strategy

### Primary hosted LLM

Use **Gemini via Google AI Studio** for hosted AI tasks.
Keep the LLM layer lightweight and structured.
Prefer one structured call for classification + extraction when possible, and one grounded call for action-plan generation.

### Backup local/open-weight LLM

Use a local open-weight model only as a fallback when hosted access is unavailable.
Recommended fallback: **Qwen2.5-7B-Instruct**.

### Provider abstraction

All AI code should go through a provider wrapper.
Do not hardcode one vendor’s SDK throughout the codebase.
Keep classifier / extractor / explainer thin and replaceable.

### Latency goals

Keep the critical path fast.
Priority order:

1. deterministic traversal/ranking
2. one structured AI pass for unstructured input
3. one grounded AI pass for the action plan

Cache repeated calls when possible.
Do not re-call the model for the same session unless the input changes.

## Current Backend Behavior

The backend already exposes:

* `GET /health`
* `POST /api/intake`
* `GET /api/results/{session_id}`

The graph is loaded from the JSON snapshot and the demo program files.
The ranking pipeline is already working and should not be destabilized.

## Frontend Behavior

### IntakePage

A three-step intake wizard:

1. Basic Info
2. Needs & Urgency
3. Free text

On submit:

* POST the intake to `/api/intake`
* store `session_id`
* redirect to `/results/{session_id}`
* poll `/api/results/{session_id}` until the result is ready

### ResultsPage

Display:

* classified intent badge
* ranked program cards
* eligibility percentage
* speed badge
* program type badge
* max amount
* expandable criteria breakdown
* documents needed
* application link
* action plan
* fairness flags if present
* data freshness indicator

## Demo Fixtures

Two demo profiles must remain strong and visually impressive:

### Maria A.

* home-based artisan bakery
* LA 90011
* approximately $35k/year
* self-employed
* urgent need: equipment, mixer broke, needs to fulfill orders next week

Expected top behavior:

* equipment-focused grant should rank highly
* fast funding should appear near the top

### David B.

* independent home healthcare aide (1099)
* approximately $48k/year
* urgent need: cash flow gap, reimbursement lag, bills due today

Expected top behavior:

* healthcare relief should rank highly
* short-term support and quick funding should be emphasized

## Environment Variables

Use `.env.example` as the template.

Common backend variables:

* `GEMINI_API_KEY`
* `GEMINI_MODEL`
* `ENVIRONMENT=development|production`
* `GRAPH_SNAPSHOT_PATH=backend/data/graph_snapshot.json`
* `LOG_LEVEL=INFO`

If a local model fallback is enabled, keep its configuration separate and optional.

## Development Setup

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Graph build:

```bash
python scripts/build_graph.py
```

## Code Quality Rules for Frontend Work

* Use TypeScript props types for all components
* Keep components small and focused
* Reuse shared UI building blocks where possible
* Keep the UI polished but not overcomplicated
* Do not change backend contracts without a reason
* Preserve the current API response shapes

## What This Is Not

* Not a chatbot
* Not a general financial advisor
* Not nationwide; scope is LA County only for this hackathon build
* Not dependent on live PayPal API integration; any PayPal-related entries are static knowledge graph entries or demo-grounded data

## Hackathon Build Order

1. Seed program data and validate graph snapshot
2. Finalize backend traversal/ranking if needed
3. Integrate AI provider abstraction and fallback logic
4. Build frontend intake wizard
5. Build results page and cards
6. Wire loading states and polling
7. Polish visuals and demo flow
8. Test Maria and David end to end
9. Presentation prep

## Final Rule

When in doubt, protect the working backend and move forward on the frontend.
Keep the demo credible, explainable, and fast.
