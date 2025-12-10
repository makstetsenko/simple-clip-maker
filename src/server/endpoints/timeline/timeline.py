from fastapi import APIRouter
import yaml

config_path = "/Users/maximstecenko/Projects/timeline_config.yaml"

router = APIRouter(
    prefix="/api/timeline",
    tags=["timeline"]
)


@router.get("/config")
async def get_timeline_config():
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
