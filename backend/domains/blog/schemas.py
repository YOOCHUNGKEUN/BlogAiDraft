from pydantic import BaseModel


class BlogRequest(BaseModel):
    github_url: str
    post_type: str
    github_token: str = ""
    branch: str = ""

