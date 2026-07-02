import httpx
from fastapi import HTTPException

from domains.blog.constants import (
    GITHUB_API_ACCEPT_HEADER,
    GITHUB_TREE_BRANCH,
    MAX_REPO_FILES,
    PRIORITY_FILE_NAMES,
    SUPPORTED_SOURCE_EXTENSIONS,
)

# 입력된 깃헙 링크 필터및 파싱하는 함수
def parse_github_url(url: str) -> tuple[str, str]:
    parts = url.strip("/").replace(".git", "").split("/")
    if "github.com" not in parts:
        raise ValueError("올바른 GitHub URL이 아닙니다")
    idx = parts.index("github.com")
    if len(parts) <= idx + 2:
        raise ValueError("올바른 GitHub URL이 아닙니다")
    owner = parts[idx + 1]
    repo = parts[idx + 2]
    if not owner or not repo:
        raise ValueError("올바른 GitHub URL이 아닙니다")
    return owner, repo


def build_github_headers(token: str = "") -> dict[str, str]:
    headers = {"Accept": GITHUB_API_ACCEPT_HEADER}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


async def fetch_repo_contents(owner: str, repo: str, path: str = "", token: str = "") -> list:
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = build_github_headers(token)

    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="GitHub repo 접근 실패. Private repo라면 Token을 확인해주세요",
            )
        return response.json()


async def fetch_file_content(download_url: str) -> str:
    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(download_url)
        return response.text


def is_supported_source_file(path: str) -> bool:
    return path.endswith(SUPPORTED_SOURCE_EXTENSIONS)


def sort_repo_files(file: dict) -> tuple[int, int, str]:
    path = file["path"]
    name = path.rsplit("/", 1)[-1]
    priority = 0 if name in PRIORITY_FILE_NAMES else 1
    depth = path.count("/")
    return priority, depth, path


async def collect_project_files(owner: str, repo: str, token: str = "") -> str:
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{GITHUB_TREE_BRANCH}?recursive=1"
    headers = build_github_headers(token)

    async with httpx.AsyncClient() as client_http:
        response = await client_http.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="GitHub repo 트리 접근 실패")

        tree = response.json().get("tree", [])
        source_files = [
            file
            for file in tree
            if file["type"] == "blob" and is_supported_source_file(file["path"])
        ]

        result = ""
        for file in sorted(source_files, key=sort_repo_files)[:MAX_REPO_FILES]:
            file_url = (
                f"https://raw.githubusercontent.com/{owner}/{repo}/"
                f"{GITHUB_TREE_BRANCH}/{file['path']}"
            )
            file_response = await client_http.get(file_url, headers=headers)
            result += f"\n\n// 파일: {file['path']}\n{file_response.text}"

        return result
