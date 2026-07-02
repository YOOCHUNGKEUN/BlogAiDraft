from fastapi import FastAPI, HTTPException
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from domains.blog.constants import OPENAI_MAX_OUTPUT_TOKENS, OPENAI_MODEL
from domains.blog.github import collect_kt_files, parse_github_url
from domains.blog.prompt import build_blog_prompt
from domains.blog.schemas import BlogRequest

# python-dotenv가 OPENAI_API_KEY를 환경변수로 로드
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 클라이언트가 자동으로 OPENAI_API_KEY 읽음
client = OpenAI()


@app.post("/generate")
async def generate_blog(request: BlogRequest):
    try:
        owner, repo = parse_github_url(request.github_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    code = await collect_kt_files(owner, repo, token=request.github_token)
    if not code:
        raise HTTPException(status_code=400, detail="Kotlin 파일을 찾을 수 없습니다")
    prompt = build_blog_prompt(request, code)
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=prompt,
        max_output_tokens=OPENAI_MAX_OUTPUT_TOKENS,
    )
    return {"result": response.output_text}


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
