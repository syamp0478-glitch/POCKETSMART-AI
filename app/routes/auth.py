from fastapi import APIRouter, Depends, HTTPException
from app.database import connect
from app.schemas import RegisterInput, LoginInput, TokenResponse
from app.security import hash_password, verify_password, create_access_token, get_current_user, get_optional_user

router = APIRouter(tags=["account"])


def token_for(row) -> TokenResponse:
    user = {"id": row["id"], "name": row["name"], "email": row["email"]}
    return TokenResponse(access_token=create_access_token(user["id"], user["email"]), user=user)


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterInput):
    with connect() as db:
        try:
            cur = db.execute("INSERT INTO users(email, name, password_hash) VALUES (?, ?, ?)",
                             (payload.email.lower(), payload.name.strip(), hash_password(payload.password)))
        except Exception as exc:
            if "UNIQUE" in str(exc):
                raise HTTPException(status_code=409, detail="An account with this email already exists") from exc
            raise
        row = db.execute("SELECT id, name, email FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return token_for(row)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginInput):
    with connect() as db:
        row = db.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return token_for(row)


@router.post("/logout")
def logout():
    # Bearer tokens are stateless; the browser clears its token on logout.
    return {"message": "Signed out. Clear the saved token in this browser."}


@router.post("/token", response_model=TokenResponse)
def issue_token(payload: LoginInput):
    return login(payload)


@router.get("/session-info")
def session_info(user: dict | None = Depends(get_optional_user)):
    return {"authenticated": user is not None, "user": user}


@router.get("/session-data")
def session_data(user: dict = Depends(get_current_user)):
    with connect() as db:
        count = db.execute("SELECT COUNT(*) FROM recommendations WHERE user_id = ?", (user["id"],)).fetchone()[0]
    return {"user": user, "saved_recommendations": count}
