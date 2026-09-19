from urllib.parse import urlparse
from app.config import settings

class AuthorizationError(ValueError): pass

def authorize_target(target: str, authorization_id: str) -> str:
    if not authorization_id:
        raise AuthorizationError("Explicit authorization is required")
    parsed = urlparse(target)
    if parsed.scheme not in {"http","https"} or not parsed.hostname:
        raise AuthorizationError("Only canonical HTTP(S) targets are supported")
    host = parsed.hostname.lower().rstrip(".")
    if host not in settings.host_allowlist:
        raise AuthorizationError("Target host is not in the authorized allowlist")
    if parsed.username or parsed.password:
        raise AuthorizationError("Credential-bearing target URLs are prohibited")
    return target
