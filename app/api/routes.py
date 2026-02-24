import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import ProvisionRequestIn, RemediateIn
from app.db.database import get_db
from app.db.models import ProvisionRequest, Decision, AuditLog
from app.policy.opa import check_allow
from app.ai.decision_engine import decide
from app.kafka.client import publish_event
from app.controllers.remediator import execute

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/provision")
async def provision(req: ProvisionRequestIn, db: Session = Depends(get_db)):
    request_id = str(uuid.uuid4())
    pr = ProvisionRequest(
        id=request_id,
        service=req.service,
        environment=req.environment,
        risk_profile=req.risk_profile,
        payload=req.model_dump(),
        status="submitted",
    )
    db.add(pr)
    db.add(AuditLog(id=str(uuid.uuid4()), request_id=request_id, actor="client", action="provision.submitted", details=req.model_dump()))
    db.commit()

    policy = await check_allow(req.model_dump())
    ai = await decide(req.model_dump(), policy)

    allowed = bool(policy.get("allow"))
    decision_id = str(uuid.uuid4())
    d = Decision(
        id=decision_id,
        request_id=request_id,
        allowed=allowed,
        risk_score=float(ai.get("risk_score", 0.0)),
        summary=str(ai.get("summary", "")),
        plan=ai.get("plan", {}),
    )
    db.add(d)
    db.add(AuditLog(id=str(uuid.uuid4()), request_id=request_id, actor="system", action="decision.created",
                    details={"allowed": allowed, "risk_score": d.risk_score, "policy": policy}))
    pr.status = "allowed" if allowed else "denied"
    db.commit()

    publish_event(topic="infra.events", event={
        "type": "provision.request",
        "request_id": request_id,
        "service": req.service,
        "environment": req.environment,
        "allowed": allowed,
        "risk_score": d.risk_score,
    })

    return {"request_id": request_id, "allowed": allowed, "risk_score": d.risk_score, "policy": policy}

@router.get("/ai/explain")
def explain(request_id: str, db: Session = Depends(get_db)):
    dec = db.query(Decision).filter(Decision.request_id == request_id).order_by(Decision.created_at.desc()).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")
    return {"request_id": request_id, "allowed": dec.allowed, "risk_score": dec.risk_score, "summary": dec.summary, "plan": dec.plan}

@router.post("/ai/remediate")
def remediate(body: RemediateIn, db: Session = Depends(get_db)):
    dec = db.query(Decision).filter(Decision.request_id == body.request_id).order_by(Decision.created_at.desc()).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")
    if dec.risk_score > body.max_risk:
        db.add(AuditLog(id=str(uuid.uuid4()), request_id=body.request_id, actor=body.actor, action="remediate.blocked",
                        details={"risk_score": dec.risk_score, "max_risk": body.max_risk}))
        db.commit()
        raise HTTPException(status_code=403, detail="Risk too high for auto remediation; require approval")

    result = execute(dec.plan or {})
    db.add(AuditLog(id=str(uuid.uuid4()), request_id=body.request_id, actor=body.actor, action="remediate.executed", details=result))
    db.commit()
    publish_event(topic="infra.events", event={"type": "remediation.executed", "request_id": body.request_id, "result": result})
    return {"request_id": body.request_id, "result": result}
