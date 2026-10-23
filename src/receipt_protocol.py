"""Development-only HMAC receipt protocol; no production transport.

A receipt is bound to action ID, exact payload digest, issuer and expiry.
The verifier must receive its secret from a trusted caller, never a request.
"""
import hashlib
import hmac
import json
import time


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sign_receipt(action_id, payload, secret, issuer="local-receiver", expires_at=None):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("receiver secret must be at least 32 bytes")
    if not isinstance(action_id, str) or not action_id.strip() or not isinstance(payload, dict) or not payload:
        raise ValueError("invalid action or payload")
    if not isinstance(issuer, str) or not issuer.strip():
        raise ValueError("issuer required")
    if expires_at is None or not isinstance(expires_at, int) or isinstance(expires_at, bool):
        raise ValueError("integer expires_at required")
    body = {"action_id": action_id, "payload_sha256": hashlib.sha256(canonical(payload)).hexdigest(),
            "issuer": issuer, "expires_at": expires_at}
    return {"body": body, "signature": hmac.new(secret, canonical(body), hashlib.sha256).hexdigest()}


def verify_receipt(envelope, action_id, payload, secret, issuer="local-receiver", now=None):
    if not isinstance(envelope, dict) or set(envelope) != {"body", "signature"}:
        return False
    body, signature = envelope["body"], envelope["signature"]
    if not isinstance(body, dict) or set(body) != {"action_id", "payload_sha256", "issuer", "expires_at"}:
        return False
    if not isinstance(signature, str) or len(signature) != 64:
        return False
    if not isinstance(secret, bytes) or len(secret) < 32:
        return False
    if not isinstance(action_id, str) or not isinstance(payload, dict):
        return False
    expiry = body["expires_at"]
    if not isinstance(expiry, int) or isinstance(expiry, bool) or expiry <= (time.time() if now is None else now):
        return False
    if body["action_id"] != action_id or body["issuer"] != issuer:
        return False
    if not hmac.compare_digest(body["payload_sha256"], hashlib.sha256(canonical(payload)).hexdigest()):
        return False
    expected = hmac.new(secret, canonical(body), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
