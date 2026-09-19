from app.compliance.catalog import assess
def test_missing_evidence_does_not_pass():
    rows=assess([])
    assert all(x["status"]=="evidence-gap" for x in rows)
