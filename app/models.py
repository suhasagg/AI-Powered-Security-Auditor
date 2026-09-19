from pydantic import BaseModel, Field
from typing import Literal

Severity = Literal["info","low","medium","high","critical"]

class Finding(BaseModel):
    finding_id: str
    source: str
    rule_id: str
    title: str
    severity: Severity
    asset: str
    evidence: str
    taxonomy: list[str] = []

class ScanRequest(BaseModel):
    tenant_id: str
    target: str
    authorization_id: str = Field(min_length=3)

class CodeRequest(BaseModel):
    tenant_id: str
    repository: str
    path: str
    content: str = Field(max_length=200_000)

class LogRequest(BaseModel):
    tenant_id: str
    lines: list[str] = Field(max_length=10_000)

class ComplianceRequest(BaseModel):
    tenant_id: str
    evidence_keys: list[str]

class AgentResult(BaseModel):
    agent: str
    status: Literal["ok","denied","unavailable"]
    summary: str
    findings: list[Finding] = []
    metadata: dict = {}
