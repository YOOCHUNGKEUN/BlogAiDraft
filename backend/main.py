from fastapi import FastAPI, HTTPException
from anthropic import Anthropic, AnthropicError
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from domains.blog.constants import CLAUDE_MAX_TOKENS, CLAUDE_MODEL
from domains.blog.github import collect_project_files, parse_github_url
from domains.blog.prompt import build_blog_prompt
from domains.blog.schemas import BlogRequest

# python-dotenv가 ANTHROPIC_API_KEY를 환경변수로 로드
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 클라이언트가 자동으로 ANTHROPIC_API_KEY 읽음
client = Anthropic()


@app.post("/generate")
async def generate_blog(request: BlogRequest):
    try:
        owner, repo = parse_github_url(request.github_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    code = await collect_project_files(owner, repo, token=request.github_token)
    if not code:
        raise HTTPException(status_code=400, detail="분석할 수 있는 프로젝트 파일을 찾을 수 없습니다")
    prompt = build_blog_prompt(request, code)
    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except AnthropicError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Claude API 호출 실패: {str(e)}",
        )
    return {"result": message.content[0].text}


@app.get("/health")
async def health():
    return {"message": "BlogDraftAI 서버 정상 동작 중"}


if FRONTEND_DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")


@app.get("/")
async def root():
    return {
        "message": "프론트엔드 빌드 파일이 없습니다. frontend에서 npm run build를 먼저 실행해주세요."
    }
