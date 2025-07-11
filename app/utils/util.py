from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from jose import jwt, JWTError, ExpiredSignatureError
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or "super secret secrets"  # load from config

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid token"}), 401
        token = auth.split()[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            customer_id = payload['sub']
        except ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except JWTError as e:
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401
        return f(customer_id=customer_id, *args, **kwargs)
    return decorated
