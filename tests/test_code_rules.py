from app.scanners.code_rules import analyze
def test_tls_rule():
    f=analyze("repo:a.py","requests.get(url, verify=False)")
    assert any(x.rule_id=="SEC001" for x in f)
