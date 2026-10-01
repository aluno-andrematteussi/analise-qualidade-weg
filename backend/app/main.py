from backend.app.config import API_TITLE, API_VERSION, BASE_DIR
from backend.app.routers import causes, pareto, scrap
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="Backend Analítico de Gestão de Qualidade e Scrap WEG (W12 / W22)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


# Servir arquivos estáticos do frontend (se a pasta existir)
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")