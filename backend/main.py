from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from anthropic import Anthropic
from dotenv import load_dotenv
from pathlib import Path
import httpx
from fastapi.middleware.cors import CORSMiddleware


load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

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
당신은 한국 개발자 기술 블로그를 실제 발행 가능한 수준으로 다듬는 시니어 테크니컬 라이터입니다.
아래 GitHub 레포지토리의 Kotlin 코드를 분석해 Velog에 바로 붙여넣을 수 있는 한국어 기술 블로그 초안을 작성해주세요.

포스트 유형: {request.post_type}
레포지토리: {request.github_url}

코드:
{code[:8000]}

작성 원칙:
- 단순한 코드 요약이 아니라, 개발자가 직접 만든 프로젝트를 소개하는 자연스러운 블로그 글로 작성합니다.
- 제목과 섹션 제목에는 Velog에서 읽기 좋은 마크다운을 사용하되, 불필요한 장식이나 과한 목록 나열은 피합니다.
- 각 섹션은 실제 경험담처럼 문단 중심으로 작성하고, 독자가 왜 이 앱을 만들었는지 공감할 수 있게 씁니다.
- 코드에서 확인 가능한 내용은 구체적으로 연결하고, 확인되지 않는 내용은 단정하지 말고 "확장할 수 있다", "이런 방향으로 볼 수 있다"처럼 표현합니다.
- "핵심 구현 - 프롬프트 설계" 섹션을 가장 깊게 작성합니다.
- 가능한 경우 짧은 코드 예시나 요청/응답 예시를 포함하되, 전체 코드를 길게 복붙하지 않습니다.
- 반드시 7번 "결과 & 회고"까지 작성하고, 마지막 문장은 완결된 문장으로 끝냅니다.
- 길이가 부족할 것 같으면 각 섹션의 문단 수를 줄이더라도 전체 구조를 끝까지 완성합니다.
- 최종 결과는 블로그 본문만 출력하고, 별도 설명이나 사족은 붙이지 않습니다.

아래 구조를 반드시 따르세요:

# 제목

검색 유입을 고려해 구체적인 제목을 작성합니다.
예시 톤:
- Claude API로 벨로그 초안을 자동 생성하는 앱을 만들어봤다 - BlogDraftAI
- FastAPI + Claude API + Flutter로 블로그 초안 자동화 앱 만들기

## 목차

- TL;DR
- 왜 만들었나
- 기술 스택 & 왜 이렇게 골랐나
- 핵심 구현 - 프롬프트 설계
- 핵심 구현 - 서버/앱 연동
- 삽질 & 트레이드오프
- 결과 & 회고

## 1. TL;DR

3줄 요약으로 작성합니다.
무엇을 만들었는지, 어떤 기술로 만들었는지, 결과가 어땠는지 핵심만 씁니다.

## 2. 왜 만들었나

블로그를 써야 하지만 초안 작성이 병목이 되는 실제 경험에서 출발해 작성합니다.
"이런 게 있으면 좋겠다"에서 직접 만들기로 이어지는 계기를 자연스럽게 풀어냅니다.
독자 공감을 얻는 핵심 섹션이므로 너무 짧게 쓰지 않습니다.

## 3. 기술 스택 & 왜 이렇게 골랐나

FastAPI를 선택한 이유를 Django/Flask와 비교해 설명합니다.
Claude API를 선택한 이유와 프롬프트 엔지니어링 방향을 설명합니다.
앱 클라이언트가 있다면 Flutter 같은 크로스플랫폼 선택 이유도 연결하고, 코드에서 확인되지 않으면 향후 클라이언트 확장 관점으로 다룹니다.
텍스트 기반 아키텍처 다이어그램을 포함합니다.

예시:
앱/웹 화면 -> FastAPI 서버 -> GitHub 코드 수집 -> Claude API -> 블로그 초안 응답 -> Velog 포맷으로 정리

## 4. 핵심 구현 - 프롬프트 설계

어떤 입력을 받아 어떤 출력을 만드는지 설명합니다.
키워드/개요/코드 분석 결과가 어떻게 블로그 초안으로 바뀌는지 씁니다.
프롬프트를 개선한 과정을 v1, v2, v3처럼 비교해서 보여줍니다.
이 섹션을 가장 깊고 차별화되게 작성합니다.

## 5. 핵심 구현 - 서버/앱 연동

FastAPI 엔드포인트 설계와 요청/응답 스키마를 설명합니다.
프론트엔드 또는 앱에서 API를 호출하고 결과를 렌더링하는 흐름을 설명합니다.
어려웠던 부분 하나를 골라 코드 예시와 함께 다룹니다.
예: CORS, 에러 핸들링, private repo token, 응답 렌더링, 스트리밍 응답 확장 가능성

## 6. 삽질 & 트레이드오프

프롬프트가 원하는 톤으로 나오지 않았던 문제, 토큰 비용, 응답 속도, API 키 관리, 배포 방식 같은 현실적인 고민을 씁니다.
장점만 쓰지 말고 선택의 대가도 함께 정리합니다.

## 7. 결과 & 회고

실제로 써보면 어떤 점이 편해지는지 정리합니다.
아쉬운 점과 다음에 추가하고 싶은 기능을 씁니다.
마지막에는 GitHub 링크 자리도 포함합니다.

예:
GitHub: {request.github_url}
"""
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}])
    return {"result": message.content[0].text}


@app.get("/")
async def root():
    return {"message": "BlogDraftAI 서버 정상 동작 중"}
