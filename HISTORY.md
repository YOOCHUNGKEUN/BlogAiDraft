# History

## 2026-07-08

- 백엔드 API 호출 방식을 Claude/Anthropic 기준으로 되돌리고 `ANTHROPIC_API_KEY` 환경변수를 사용하도록 정리했습니다.

## 2026-07-02

- Claude 응답 토큰 한도와 완결 조건을 조정해 블로그 초안이 중간에 끊기는 문제를 줄였습니다.
- Claude 프롬프트를 실제 블로그 발행용 구성으로 개편했습니다.
- 프론트엔드에 GitHub private token 발급 위치와 안내 링크를 추가했습니다.
- 백엔드 파일을 `backend` 폴더로 이동해 프론트엔드와 서버 코드를 분리했습니다.
- React 기반 프론트엔드 화면을 추가해 GitHub 저장소 URL, private token, 포스트 유형 입력과 Claude 생성 결과 출력을 지원했습니다.
- 백엔드 실행 의존성을 정리한 `requirements.txt`를 추가했습니다.
- 프로젝트 실행 방법과 프론트엔드 사용 흐름을 `README.md`에 정리했습니다.
