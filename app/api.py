from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from app.models import ScanRequest, CodeRequest, LogRequest, ComplianceRequest, AgentResult
from app.orchestrator import scan_vulnerability, analyze_code, analyze_logs, check_compliance
from app.security.authorization import AuthorizationError
from app.audit.service import emit

app=FastAPI(title="AI-Powered Security Auditor",version="1.0.0",
            description="Authorization-first defensive agentic security reference architecture.")
REQ=Counter("security_auditor_requests_total","Requests",["agent","status"])
LAT=Histogram("security_auditor_latency_seconds","Latency",["agent"])

@app.get("/health")
async def health(): return {"status":"ok"}

@app.post("/v1/vulnerability/scan",response_model=AgentResult)
async def vulnerability(req: ScanRequest):
    try:
        with LAT.labels("vulnerability").time():
            result=await scan_vulnerability(req.target,req.authorization_id)
    except AuthorizationError as e:
        emit("scan_denied",req.tenant_id,"denied",{"reason":str(e)})
        raise HTTPException(403,str(e))
    REQ.labels("vulnerability",result.status).inc()
    emit("scan_completed",req.tenant_id,result.status,{"target":req.target})
    return result

@app.post("/v1/code/analyze",response_model=AgentResult)
async def code(req: CodeRequest):
    with LAT.labels("code").time(): result=await analyze_code(req.repository,req.path,req.content)
    REQ.labels("code",result.status).inc()
    emit("code_analysis_completed",req.tenant_id,result.status,{"repository":req.repository,"path":req.path})
    return result

@app.post("/v1/logs/analyze",response_model=AgentResult)
async def logs(req: LogRequest):
    with LAT.labels("logs").time(): result=await analyze_logs(req.lines)
    REQ.labels("logs",result.status).inc()
    emit("log_analysis_completed",req.tenant_id,result.status)
    return result

@app.post("/v1/compliance/check",response_model=AgentResult)
async def compliance(req: ComplianceRequest):
    with LAT.labels("compliance").time(): result=await check_compliance(req.evidence_keys)
    REQ.labels("compliance",result.status).inc()
    emit("compliance_check_completed",req.tenant_id,result.status)
    return result

@app.get("/metrics")
async def metrics(): return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
