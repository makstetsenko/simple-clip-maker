from pydantic import BaseModel


class NewProjectRequest(BaseModel):
    width: int
    height: int
    fps: int
    project_name: str
