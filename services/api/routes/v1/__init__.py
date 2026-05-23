from fastapi import APIRouter

from routes.v1.authoring import router as authoring_router
from routes.v1.pipeline import router as pipeline_router
from routes.v1.projects import router as projects_router
from routes.v1.simulations import router as simulations_router
from routes.v1.workbench import router as workbench_router

router = APIRouter(prefix="/api/v1")
router.include_router(workbench_router)
router.include_router(projects_router)
router.include_router(authoring_router)
router.include_router(pipeline_router)
router.include_router(simulations_router)
