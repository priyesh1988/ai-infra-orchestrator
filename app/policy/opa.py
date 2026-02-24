import os
import httpx

OPA_URL = os.getenv("OPA_URL", "http://localhost:8181/v1/data/infra/allow")

async def check_allow(input_doc: dict) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.post(OPA_URL, json={"input": input_doc})
        r.raise_for_status()
        data = r.json()
        # Expect: {"result": {"allow": true/false, "reason": "...", "constraints": {...}}}
        result = data.get("result", {})
        return {
            "allow": bool(result.get("allow", False)),
            "reason": result.get("reason", ""),
            "constraints": result.get("constraints", {}),
        }
