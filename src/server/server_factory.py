from fastapi import FastAPI
from .endpoints.timeline import timeline
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/files", StaticFiles(directory="/"), name="videos")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(timeline.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
