import base64
import hashlib
import hmac
import json
import secrets
import time
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings
from app.database import connect

bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_text, digest_text = encoded.split("$", 1)
        salt = base64.urlsafe_b64decode(salt_text)
        expected = base64.urlsafe_b64decode(digest_text)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, email: str) -> str:
    now = int(time.time())
    encode = lambda obj: base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode()).rstrip(b"=").decode()
    head = encode({"alg": "HS256", "typ": "JWT"})
    payload = encode({"sub": str(user_id), "email": email, "iat": now, "exp": now + settings.access_token_minutes * 60})
    message = f"{head}.{payload}"
    signature = base64.urlsafe_b64encode(hmac.new(settings.secret_key.encode(), message.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
    return f"{message}.{signature}"


def decode_access_token(token: str) -> dict:
    try:
        head, payload, signature = token.split(".")
        message = f"{head}.{payload}"
        expected = base64.urlsafe_b64encode(hmac.new(settings.secret_key.encode(), message.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
        if not hmac.compare_digest(signature, expected):
            raise ValueError("signature")
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if int(data["exp"]) < int(time.time()):
            raise ValueError("expired")
        return data
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired sign-in token") from exc


def get_optional_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    with connect() as db:
        row = db.execute("SELECT id, email, name FROM users WHERE id = ?", (payload["sub"],)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Account no longer exists")
    return dict(row)


def get_current_user(user: dict | None = Depends(get_optional_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sign in to use this feature")
    return user
