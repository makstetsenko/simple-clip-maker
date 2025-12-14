from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .endpoints.timeline import timeline
from .endpoints.project import project_endpoints
from .endpoints.media import media_endpoints

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(timeline.router)
app.include_router(project_endpoints.router)
app.include_router(media_endpoints.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
