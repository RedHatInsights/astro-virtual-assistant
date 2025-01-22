from flask import request, abort, jsonify
import base64
import functools
import json

def check_identity(identity_header):
    try:
        base64.b64decode(identity_header)
    except Exception:
        return False
    return True

def require_identity_header(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        identity_header = request.headers.get('x-rh-identity')
        if not identity_header or not check_identity(identity_header):
            return jsonify(message="Invalid x-rh-identity"), 401
        return func(*args, **kwargs)
    return wrapper

def get_org_id_from_identity(identity):
    decoded_identity = base64.b64decode(identity).decode("utf8")
    identity_json = json.loads(decoded_identity)
    identity = identity_json.get("identity", {})
    org_id = identity.get("org_id")
    return org_id
