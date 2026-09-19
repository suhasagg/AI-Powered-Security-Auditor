from app.models import AgentResult
from app.compliance.catalog import assess
from app.llm.gateway import explain

async def run(evidence_keys: list[str]) -> AgentResult:
    results=assess(evidence_keys)
    ev="\n".join(f"{x['control_id']} {x['status']} missing={x['missing']}" for x in results)
    summary=await explain("Summarize compliance evidence gaps. Do not claim certification.",ev)
    return AgentResult(agent="compliance_checker",status="ok",summary=summary,metadata={"controls":results})
