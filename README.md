# 🧠 AI Infrastructure Orchestrator
### Software-Defined Infrastructure Control Plane with AI-Assisted Remediation

> A unified framework to provision, govern, observe, and self-heal infrastructure across Kubernetes + Cloud IaC — with AI assisting (and safely gating) any manual interventions.

---

## Why this exists

Most infra stacks today are a *collection* of tools:
- Terraform for provisioning
- Helm/Argo CD for delivery
- OPA/Kyverno for policy
- Prometheus/Grafana for metrics
- Loki for logs
- Jaeger for traces
- Kafka for events
- Postgres for system state

This repo stitches those into **one cohesive control-plane**:
- One API to request infra changes
- One policy layer to enforce guardrails
- One event bus to react to drift/anomalies
- One AI layer to explain + recommend + (optionally) remediate
- One audit trail to satisfy SOC2-style evidence

---

## 🏗 Architecture (real-world components)

```
Client / ChatOps
   │
   ▼
FastAPI Control API  ──────────────►  PostgreSQL (requests, decisions, audit)
   │                                    │
   │                                    ▼
   │                              Grafana dashboards
   │
   ▼
Policy Engine (OPA)  ──────────────►  Decision: allow/deny + constraints
   │
   ▼
Event Bus (Kafka)  ────────────────►  Consumers: drift, remediator, telemetry hooks
   │
   ▼
Drift & Signals (K8s + IaC) ───────►  AI Decision Engine (OpenAI or Ollama)
   │                                    │
   ▼                                    ▼
Remediation Controllers           Explanation + runbooks + gated actions
(Terraform/Helm/Argo)
   │
   ▼
Kubernetes / Cloud Infra  ────────► Observability: Prometheus + Loki + Jaeger
```

---

## ✅ What’s included in this repo

### Control plane
- **FastAPI** control API (request, plan, remediate, explain)
- **PostgreSQL** persistence (deployments, decisions, audit logs)
- **Kafka** event bus (drift + remediation events)
- **OPA** policy checks (allow/deny and constraints)
- **AI** engine (OpenAI if key exists, otherwise **Ollama** fallback)
- **Audit logging**: immutable-ish event log table + structured JSON logs

### Delivery & infra
- **Helm chart** for deploying the control plane on Kubernetes
- **Argo CD** app manifest example (GitOps)
- **Terraform** module skeletons (network, k8s, storage)
- **Kubernetes** network policy examples (default-deny)

### Observability
- **Prometheus** scrape config for API metrics
- **Grafana** provisioning (datasources + dashboards stub)
- **OpenTelemetry** traces → **Jaeger**
- **Loki** log aggregation (docker-compose)

---

## 🧪 Local quickstart (Docker Compose)

### 1) Start everything
```bash
docker compose up --build
```

### 2) Health check
```bash
curl http://localhost:8000/health
```

### 3) Submit a provisioning request
```bash
curl -X POST http://localhost:8000/provision   -H "Content-Type: application/json"   -d '{
    "service": "payment-api",
    "environment": "prod",
    "replicas": 3,
    "risk_profile": "medium",
    "resources": {"cpu":"250m","memory":"256Mi"},
    "changes": {"helm_release":"payment-api","version":"1.2.3"}
  }'
```

### 4) Ask AI to explain the decision
```bash
curl "http://localhost:8000/ai/explain?request_id=<REQUEST_ID_FROM_RESPONSE>"
```

### 5) Trigger a remediation (gated)
```bash
curl -X POST "http://localhost:8000/ai/remediate"   -H "Content-Type: application/json"   -d '{
    "request_id":"<REQUEST_ID>",
    "mode":"auto",
    "max_risk":0.6
  }'
```

---

## 🔐 AI safety model

AI never blindly executes.
- AI generates: **risk score**, **plan**, **commands**, **justification**
- OPA validates that the plan is **within constraints**
- Policy + thresholds decide:
  - **auto** (risk <= threshold)
  - **approve** (human approval required)
  - **deny**

---

## 📦 Repo layout

```
ai-infra-orchestrator/
├── app/                      # FastAPI control plane
│   ├── main.py
│   ├── api/                  # routers
│   ├── ai/                   # LLM + risk model
│   ├── policy/               # OPA hooks
│   ├── drift/                # drift detectors (k8s/terraform)
│   ├── kafka/                # producer/consumer helpers
│   ├── db/                   # SQLAlchemy models + migrations-lite
│   └── observability/        # OTEL + metrics
├── policies/                 # OPA policies (Rego)
├── helm/ai-infra-orchestrator/
├── argo/app.yaml
├── terraform/                # module skeletons
├── observability/            # prometheus/grafana/loki/jaeger configs
├── docker-compose.yml
├── .github/workflows/ci.yml
├── Makefile
└── README.md
```

---

## 🚀 Kubernetes (Helm)

```bash
helm upgrade --install ai-infra-orchestrator ./helm/ai-infra-orchestrator   --namespace platform --create-namespace
```

---

## 🧩 Notes
- This repo is a production-grade *starting point* with real components wired end-to-end.
- Terraform modules are skeletons you can plug into your cloud (AWS/GCP/Azure/on-prem).
- AI execution is safe-gated by policy + thresholds.

---

## License
MIT
