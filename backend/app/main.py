from backend.app.config import API_TITLE, API_VERSION, BASE_DIR
from backend.app.routers import causes, pareto, scrap
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Backend Analítico de Gestão de Qualidade e Scrap WEG (W12 / W22)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", "http://127.0.0.1:3000",
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5500", "http://127.0.0.1:5500",
        "http://localhost:8000", "http://127.0.0.1:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão dos módulos de endpoints
app.include_router(pareto.router)
app.include_router(scrap.router)
app.include_router(causes.router)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": API_TITLE, "engine": "DuckDB + Parquet"}


# O HTML atual está em frontend/html e ainda não existe um index.html na raiz.
frontend_dir = BASE_DIR / "frontend" / "html"


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(frontend_dir / "code.html")


if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend")
