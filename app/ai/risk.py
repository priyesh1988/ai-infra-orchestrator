def risk_score(payload: dict, policy_constraints: dict) -> float:
    # Simple, explainable baseline risk model:
    # - prod increases risk
    # - large replica counts increase risk
    # - privileged/hostNetwork/hostPath bumps risk if present
    env = (payload.get("environment") or "dev").lower()
    replicas = int(payload.get("replicas") or 1)
    risk = 0.2
    if env == "prod":
        risk += 0.2
    if replicas >= 10:
        risk += 0.2
    if replicas >= 50:
        risk += 0.2
    cfg = payload.get("changes") or {}
    if cfg.get("privileged") is True or cfg.get("hostNetwork") is True or cfg.get("hostPath") is True:
        risk += 0.3
    # Constraints can reduce risk if enforced (example: max replicas)
    max_rep = policy_constraints.get("max_replicas")
    if max_rep is not None and replicas <= int(max_rep):
        risk -= 0.05
    return max(0.0, min(1.0, risk))
