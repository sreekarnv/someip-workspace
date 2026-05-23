from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.v1 import router as v1_router
from schemas.workflow import HealthResponse

app = FastAPI(title="SOME/IP Simulation Studio", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(v1_router)


@app.get("/health", response_model=HealthResponse, operation_id="getHealth")
async def health():
    return {"status": "ok", "api": "v1"}
