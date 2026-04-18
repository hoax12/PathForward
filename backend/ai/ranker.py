# backend/ai/ranker.py

from typing import List
from schemas import ProgramMatch, ClassifiedIntent

INTENT_KEYWORDS = {
    "equipment_emergency": ["equipment", "mixer", "repair", "replacement"],
    "cashflow_gap": ["cashflow", "working capital", "reimbursement", "bill"],
    "housing_need": ["housing", "rent", "eviction", "shelter"],
}

def get_speed_score(speed: str) -> float:
    scores = {
        "same_day": 1.0,
        "1-3_days": 0.8,
        "1-2_weeks": 0.5,
        "varies": 0.3
    }
    return scores.get(speed, 0.0)

def rank_matches(
    matches: List[ProgramMatch], 
    intent: ClassifiedIntent,
    top_k: int = 5
) -> List[ProgramMatch]:
    """
    Deterministically re-rank the raw graph matches using composite scoring 
    and intent alignment.
    """
    scored_matches = []
    
    # Map full intent to keywords for better matching, fallback to basic split if not mapped
    intent_key = intent.primary_intent.lower()
    keywords = INTENT_KEYWORDS.get(intent_key, [intent_key.split('_')[0]])

    for match in matches:
        # 1. Base Architecture Formula
        eligibility = match.eligibility_score * 0.4
        speed = get_speed_score(match.speed_to_fund) * 0.3
        
        # Normalize impact (assuming $50k is a reasonable max for micro-businesses)
        impact = min((match.max_amount or 0) / 50000.0, 1.0) * 0.2
        
        # Calculate friction (fewer documents = higher score)
        doc_count = len(match.documents_needed)
        friction = max(1.0 - (doc_count * 0.2), 0.0) * 0.1

        # 2. Intent Alignment Boost (The Tie-Breaker Fix)
        intent_boost = 0.0
        program_text_pool = f"{match.name} {match.org_name} {' '.join(match.documents_needed)}".lower()
        
        if any(keyword in program_text_pool for keyword in keywords):
            intent_boost += 0.15
            
        # 3. Compute Composite Score
        composite_score = eligibility + speed + impact + friction + intent_boost
        
        # Attach the temporary score for sorting (you can strip this before returning if desired)
        scored_matches.append((composite_score, match))

    # Sort descending by composite score
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    
    # Return the top K ProgramMatch objects
    return [match for score, match in scored_matches[:top_k]]