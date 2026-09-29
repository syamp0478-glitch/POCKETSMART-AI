import json
from fastapi import APIRouter, Depends, HTTPException
from app.database import connect
from app.security import get_current_user

router = APIRouter(tags=["history"])


@router.get("/history")
def history(user: dict = Depends(get_current_user)):
    with connect() as db:
        rows = db.execute("SELECT id, planner, request_json, result_json, created_at FROM recommendations "
                          "WHERE user_id = ? ORDER BY id DESC LIMIT 50", (user["id"],)).fetchall()
    return [{"id": row["id"], "planner": row["planner"], "request": json.loads(row["request_json"]),
             "result": json.loads(row["result_json"]), "created_at": row["created_at"]} for row in rows]


@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id: int, user: dict = Depends(get_current_user)):
    with connect() as db:
        row = db.execute("SELECT id, planner, request_json, result_json, created_at FROM recommendations "
                         "WHERE id = ? AND user_id = ?", (recommendation_id, user["id"])).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"id": row["id"], "planner": row["planner"], "request": json.loads(row["request_json"]),
            "result": json.loads(row["result_json"]), "created_at": row["created_at"]}
