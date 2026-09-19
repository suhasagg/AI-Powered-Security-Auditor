from app.detection.logs import detect
def test_auth_burst():
    f=detect(["login failed"]*5)
    assert any(x.rule_id=="LOG001" for x in f)
