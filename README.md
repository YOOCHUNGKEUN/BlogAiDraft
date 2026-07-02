# BlogDraftAI API

GitHub 저장소의 Kotlin 코드를 수집해 OpenAI API로 전달하고, 한국어 기술 블로그 초안을 생성하는 프로젝트입니다. `backend` 폴더에는 FastAPI 서버가 있고, `frontend` 폴더에는 저장소 URL, GitHub private token, 포스트 유형을 입력하고 결과를 확인할 수 있는 React 화면이 있습니다.

## 프로젝트 구조

```text
BlogDraftAI_API/
├─ backend/
│  ├─ domains/
│  │  └─ blog/
│  │     ├─ constants.py
│  │     ├─ github.py
│  │     ├─ prompt.py
│  │     └─ schemas.py
│  ├─ main.py
│  ├─ requirements.txt
│  └─ .env
├─ frontend/
│  ├─ package.json
│  ├─ index.html
│  └─ src/
├─ README.md
└─ HISTORY.md
```

## 실행 준비

백엔드 의존성을 설치합니다.

```powershell
cd backend
py -m pip install -r requirements.txt
```

`backend/main.py`와 같은 위치에 `backend/.env` 파일을 만들고 OpenAI API 키를 등록합니다.

```env
OPENAI_API_KEY=여기에_OpenAI_API키
```

## 백엔드 실행

```powershell
cd D:\Chongfolder\project\branch\blogdragf_ai-workspace\BlogDraftAI_API\backend
py -m uvicorn main:app --reload
```

확인 주소:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## 일반 실행: 백엔드에서 웹까지 같이 보기

프론트엔드를 한 번 빌드하면 FastAPI가 `frontend/dist`를 같이 서빙합니다.

```powershell
cd D:\Chongfolder\project\branch\blogdragf_ai-workspace\BlogDraftAI_API\frontend
npm.cmd install
npm.cmd run build
```

그 다음 백엔드를 실행하고 브라우저에서 `http://127.0.0.1:8000`으로 접속합니다.

## 개발 실행: 프론트엔드만 따로 켜기

```powershell
cd D:\Chongfolder\project\branch\blogdragf_ai-workspace\BlogDraftAI_API\frontend
npm.cmd install
npm.cmd run dev
```

기본 프론트엔드 주소는 Vite 실행 로그에 표시됩니다. 개발 서버는 `/generate` 요청을 `http://127.0.0.1:8000/generate`로 프록시합니다.

## 사용 방법

1. 백엔드 서버를 먼저 실행합니다.
2. 프론트엔드 개발 서버를 실행합니다.
3. GitHub 저장소 URL을 입력합니다.
4. private 저장소라면 GitHub token을 입력합니다.
5. 포스트 유형을 선택하고 초안 생성을 실행합니다.

현재 백엔드는 Kotlin `.kt` 파일을 대상으로 코드를 수집합니다. 생성 결과는 TL;DR, 제작 계기, 기술 스택, 프롬프트 설계, 서버/앱 연동, 트레이드오프, 회고 순서의 실제 블로그 발행용 구조로 작성됩니다. 응답 길이를 넉넉히 설정해 글이 중간에 끊기지 않고 회고까지 마무리되도록 구성했습니다.

## GitHub Private Token 안내

Public 저장소는 token 없이 사용할 수 있습니다. Private 저장소를 분석하려면 GitHub Personal Access Token이 필요합니다.

토큰 생성 위치:

- `GitHub > Settings > Developer settings > Personal access tokens`
- 바로가기: `https://github.com/settings/tokens`

Private 저장소 접근이 필요하면 토큰 권한에서 저장소 접근 권한을 포함해야 합니다. 발급한 토큰은 프론트엔드의 `GitHub Private Token` 입력칸에 넣어 사용합니다.
