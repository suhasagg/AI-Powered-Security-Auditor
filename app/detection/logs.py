import hashlib
from app.models import Finding

def detect(lines: list[str]) -> list[Finding]:
    lower=[x.lower() for x in lines]
    findings=[]
    failed=sum(("login failed" in x or "authentication failed" in x) for x in lower)
    errors=sum((" 500 " in f" {x} " or "status=500" in x) for x in lower)
    denied=sum(("access denied" in x or "permission denied" in x) for x in lower)
    for rule,title,count,threshold,severity in [
        ("LOG001","Authentication failure burst",failed,5,"medium"),
        ("LOG002","Server error burst",errors,5,"medium"),
        ("LOG003","Access-denied burst",denied,5,"medium"),
    ]:
        if count >= threshold:
            fp=hashlib.sha256(f"{rule}:{count}".encode()).hexdigest()[:16]
            findings.append(Finding(
                finding_id=f"log-{fp}", source="log-detector", rule_id=rule,
                title=title, severity=severity, asset="submitted-log-batch",
                evidence=f"Observed {count} matching events in the submitted batch.",
                taxonomy=[]))
    return findings
