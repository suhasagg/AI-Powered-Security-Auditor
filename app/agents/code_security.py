from app.models import AgentResult
from app.scanners.code_rules import analyze
from app.llm.gateway import explain

async def run(repository: str, path: str, content: str) -> AgentResult:
    asset=f"{repository}:{path}"
    findings=analyze(asset,content)
    ev="\n".join(f"{f.rule_id} {f.title} {f.evidence}" for f in findings) or "No demo-rule matches."
    summary=await explain("Explain the deterministic code-security findings and safe remediation",ev)
    return AgentResult(agent="code_security_analyzer",status="ok",summary=summary,findings=findings)
