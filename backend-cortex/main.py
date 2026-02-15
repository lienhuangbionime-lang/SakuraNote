from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import asyncio

# Load .env before other imports that use os.getenv
load_dotenv(".env")

from app.core.config import settings
from app.workers.embedding_worker import embedding_worker

# Lifespan Manager (Startup/Shutdown events)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Scheduling
    scheduler = BackgroundScheduler()
    scheduler.start()
    print("[SCHEDULER] Subconscious Scheduler Started")
    
    # Startup: Initialize Intelligence Workers (Option A)
    # Using create_task to run in background without blocking startup
    asyncio.create_task(embedding_worker.start())
    print("[WORKER] Subconscious Embedding Process Initiated")
    
    # Verify AI Core
    if not settings.GEMINI_API_KEY:
        print("[WARN] Application running without valid AI credentials")
        
    yield
    
    # Shutdown
    scheduler.shutdown()
    embedding_worker.is_running = False
    print("[SHUTDOWN] Systems Powering Down")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Configuration
# CORS Configuration
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.get("/")
async def root():
    return {
        "system": "LifeOS Cortex",
        "status": "Online",
        "version": "7.1-BrainLink",
        "philosophy": "Autopoiesis"
    }

from app.api.v1 import ingest, system, memories, projects, crystallize, chat, brain

app.include_router(ingest.router, prefix="/api/v1", tags=["Ingest"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(memories.router, prefix="/api/v1/memories", tags=["Memories"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(crystallize.router, prefix="/api/v1/cortex", tags=["Cortex"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(brain.router, prefix="/api/v1/brain", tags=["Brain"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)