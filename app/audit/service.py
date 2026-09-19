import logging
logger=logging.getLogger("security-audit")
def emit(event: str, tenant_id: str, outcome: str, details: dict | None=None):
    # Do not include raw source/log evidence in audit by default.
    logger.info({"event":event,"tenant_id":tenant_id,"outcome":outcome,"details":details or {}})
