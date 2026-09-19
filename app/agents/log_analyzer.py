from app.models import AgentResult
from app.detection.logs import detect
from app.llm.gateway import explain

async def run(lines: list[str]) -> AgentResult:
    findings=detect(lines)
    ev="\n".join(f"{f.title}: {f.evidence}" for f in findings) or "No configured anomaly threshold crossed."
    summary=await explain("Explain detected operational/security anomalies without taking containment actions",ev)
    return AgentResult(agent="log_analyzer",status="ok",summary=summary,findings=findings)
