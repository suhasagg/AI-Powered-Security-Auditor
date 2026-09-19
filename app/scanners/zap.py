import hashlib
from app.models import Finding
from app.config import settings
from app.security.authorization import authorize_target

async def baseline_scan(target: str, authorization_id: str) -> list[Finding]:
    authorize_target(target, authorization_id)
    if settings.zap_mode == "mock":
        fp=hashlib.sha256(target.encode()).hexdigest()[:16]
        return [Finding(
            finding_id=f"zap-{fp}", source="owasp-zap-baseline", rule_id="10020",
            title="Demo: security header review", severity="low", asset=target,
            evidence="Mock baseline finding; configure an isolated ZAP worker for authorized real assessments.",
            taxonomy=["OWASP-A05"])]
    # Production seam: submit a typed job to an isolated ZAP worker.
    # Deliberately no arbitrary shell/active-scan execution in the API process.
    raise RuntimeError("External ZAP worker is not configured")
