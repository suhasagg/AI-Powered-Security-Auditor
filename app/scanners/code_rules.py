import re, hashlib
from app.models import Finding

RULES = [
    ("SEC001", "TLS verification disabled", "high", re.compile(r"verify\s*=\s*False"), ["OWASP-A02"]),
    ("SEC002", "Dynamic eval usage", "high", re.compile(r"\beval\s*\("), ["OWASP-A03"]),
    ("SEC003", "Potential shell execution", "high", re.compile(r"\b(os\.system|subprocess\.(?:call|run|Popen))\s*\("), ["OWASP-A03"]),
    ("SEC004", "Potential hard-coded secret", "medium", re.compile(r"(?i)\b(password|api_key|secret)\s*=\s*['\"][^'\"]{6,}['\"]"), ["OWASP-A02"]),
    ("SEC005", "Potential SQL string construction", "medium", re.compile(r"(?i)(SELECT|INSERT|UPDATE|DELETE).*(\+|%s|f['\"])"), ["OWASP-A03"]),
]

def analyze(asset: str, content: str) -> list[Finding]:
    out=[]
    for rid,title,severity,pattern,tax in RULES:
        for m in pattern.finditer(content):
            fp=hashlib.sha256(f"{asset}:{rid}:{m.start()}".encode()).hexdigest()[:16]
            # Evidence intentionally avoids returning full secrets/source.
            out.append(Finding(
                finding_id=f"code-{fp}", source="code-rules", rule_id=rid,
                title=title, severity=severity, asset=asset,
                evidence=f"Pattern matched at character offset {m.start()}",
                taxonomy=tax))
    return out
