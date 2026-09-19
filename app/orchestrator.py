from app.agents import vulnerability, code_security, log_analyzer, compliance
# Explicit orchestrator facade; production version persists workflow state and uses queues.
async def scan_vulnerability(target, authorization_id): return await vulnerability.run(target,authorization_id)
async def analyze_code(repository,path,content): return await code_security.run(repository,path,content)
async def analyze_logs(lines): return await log_analyzer.run(lines)
async def check_compliance(evidence_keys): return await compliance.run(evidence_keys)
