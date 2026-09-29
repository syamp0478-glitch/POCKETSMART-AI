from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.config import settings
from app.database import init_db
from app.routes import auth, planners, history

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, description="Budget-aware planning for home, events, and jewelry.",
              version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True,
                   allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)


@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
@app.get("/register", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"app_name": settings.app_name})


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "ai_configured": bool(settings.gemini_api_key)}


@app.get("/startup")
def startup_status():
    return {"database": "ready", "ai_configured": bool(settings.gemini_api_key), "model": settings.gemini_model}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
