from .risk import risk_score
from .llm import generate

async def decide(payload: dict, policy: dict) -> dict:
    constraints = policy.get("constraints", {})
    score = risk_score(payload, constraints)

    prompt = f"""You are an infrastructure SRE assistant.
Given this provisioning request and policy outcome, produce:
1) a short decision summary
2) a remediation plan (steps) if denied or risky
3) commands/actions in a SAFE, reversible way
Return JSON with keys: summary, plan, commands.

REQUEST: {payload}
POLICY: {policy}
RISK_SCORE: {score}
"""
    llm_text = await generate(prompt)

    # Best-effort: keep plan as text; caller can store raw.
    return {
        "risk_score": score,
        "summary": "AI-generated decision summary (see raw).",
        "plan": {"raw": llm_text},
        "commands": [],
    }
