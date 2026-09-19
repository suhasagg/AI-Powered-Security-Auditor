CATALOG = {
    "AC-01": {"title":"Access control evidence", "requires":{"oidc","rbac","access-review"}},
    "AU-01": {"title":"Audit logging evidence", "requires":{"audit-log","retention-policy"}},
    "SDLC-01": {"title":"Secure SDLC evidence", "requires":{"sast","dependency-scan","secret-scan"}},
    "IR-01": {"title":"Incident response evidence", "requires":{"incident-plan","incident-test"}},
}

def assess(evidence_keys: list[str]) -> list[dict]:
    evidence=set(evidence_keys)
    results=[]
    for cid,c in CATALOG.items():
        missing=sorted(c["requires"]-evidence)
        results.append({
            "control_id":cid, "title":c["title"],
            "status":"evidence-present" if not missing else "evidence-gap",
            "missing":missing
        })
    return results
