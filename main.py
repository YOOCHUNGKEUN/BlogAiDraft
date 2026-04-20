from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
import os
import httpx
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
client = Anthropic()

class BlogRequest(BaseModel):
    github_url: str
    post_type: str
    github_token: str = ""

def parse_github_url(url: str):
    parts = url.strip("/").replace(".git", "").split("/")
    if "github.com" not in parts:
        raise ValueError("올바른 GitHub URL이 아닙니다")
    idx = parts.index("github.com")
    owner = parts[idx + 1]
    repo = parts[idx + 2]
    return owner, repo
    


async def fetch_repo_contents(owner: str, repo: str, path: str = "", token: str = "") -> list:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub repo 접근 실패. Private repo라면 Token을 확인해주세요")
        return response.json()


async def fetch_file_content(download_url: str) -> str:
    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(download_url)
        return response.text


async def collect_kt_files(owner: str, repo: str, path: str = "", depth: int = 0, token: str = "") -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub repo 트리 접근 실패")
        
        tree = response.json().get("tree", [])
        kt_files = [f for f in tree if f["path"].endswith(".kt") and f["type"] == "blob"]
        
        result = ""
        for file in kt_files[:20]:  # 최대 20개
            file_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{file['path']}"
            if token:
                file_response = await client_http.get(file_url, headers=headers)
            else:
                file_response = await client_http.get(file_url)
            result += f"\n\n// 파일: {file['path']}\n{file_response.text}"
        return result



    
@app.post("/generate")
async def generate_blog(request: BlogRequest):
    try:
        owner, repo = parse_github_url(request.github_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    code = await collect_kt_files(owner, repo, token=request.github_token)

    if not code:
        raise HTTPException(status_code=400, detail="Kotlin 파일을 찾을 수 없습니다")

    prompt = f"""
    
당신은 한국 개발자 기술 블로그 작성 전문가입니다.
아래 GitHub 레포지토리의 코드를 분석하고 Velog에 올릴 한국어 기술 포스트 초안을 작성해주세요.

포스트 유형: {request.post_type}
레포지토리: {request.github_url}

코드:
{code[:8000]}

다음 형식으로 작성해주세요:
1. 제목 (# 제목)
2. 들어가며
3. 프로젝트 구조 설명
4. 핵심 구현 내용
5. 마무리
"""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}])
    return {"result": message.content[0].text}


@app.get("/")
async def root():
    return {"message": "BlogDraftAI 서버 정상 동작 중"}