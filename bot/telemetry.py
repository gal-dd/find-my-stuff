# bot/telemetry.py
import logging

log = logging.getLogger("telemetry")

def log_event(user_id: str, action: str, **fields):
    """
    Log a structured event like:
    user=123 action=create item='כוסות' location='ארון מטבח'
    """
    # key=value pairs; quote strings with spaces
    parts = [f"user={user_id}", f"action={action}"]
    for k, v in fields.items():
        if v is None:
            continue
        vs = str(v)
        if " " in vs or "\t" in vs:
            vs = f"'{vs}'"
        parts.append(f"{k}={vs}")
    log.info(" ".join(parts))
