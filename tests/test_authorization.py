import pytest
from app.security.authorization import authorize_target, AuthorizationError

def test_allowed_target():
    assert authorize_target("https://app.internal.example","auth-1").startswith("https://")

def test_denied_target():
    with pytest.raises(AuthorizationError):
        authorize_target("https://example.com","auth-1")
