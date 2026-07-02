import React, { useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export default function App() {
  const [githubUrl, setGithubUrl] = useState("");
  const [githubToken, setGithubToken] = useState("");
  const [postType, setPostType] = useState("기술 블로그");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const canSubmit = useMemo(() => githubUrl.trim().length > 0 && !isLoading, [githubUrl, isLoading]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          github_url: githubUrl.trim(),
          post_type: postType.trim() || "기술 블로그",
          github_token: githubToken.trim()
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "블로그 초안 생성에 실패했습니다.");
      }

      setResult(data.result || "응답 결과가 비어 있습니다.");
    } catch (requestError) {
      setError(requestError.message || "요청 중 알 수 없는 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCopy() {
    if (!result) return;
    await navigator.clipboard.writeText(result);
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <div className="intro">
          <p className="eyebrow">BlogDraftAI</p>
          <h1>GitHub 코드를 블로그 초안으로 정리</h1>
          <p>
            저장소 주소와 토큰을 입력하면 FastAPI 서버가 코드를 모아 OpenAI에 전달하고,
            정리된 한국어 기술 글 초안을 반환합니다.
          </p>
        </div>

        <div className="tool-layout">
          <form className="input-panel" onSubmit={handleSubmit}>
            <label>
              <span>GitHub 저장소 URL</span>
              <input
                type="url"
                value={githubUrl}
                onChange={(event) => setGithubUrl(event.target.value)}
                placeholder="https://github.com/owner/repository"
                required
              />
            </label>

            <label>
              <span>GitHub Private Token</span>
              <input
                type="password"
                value={githubToken}
                onChange={(event) => setGithubToken(event.target.value)}
                placeholder="public 저장소는 비워둬도 됩니다"
                autoComplete="off"
              />
            </label>

            <div className="token-guide">
              <strong>Private key 어디에 있는지 모르시나요?</strong>
              <p>
                GitHub Personal Access Token을 입력하세요. GitHub Settings &gt; Developer
                settings &gt; Personal access tokens에서 만들 수 있습니다.
              </p>
              <a href="https://github.com/settings/tokens" target="_blank" rel="noreferrer">
                토큰 생성 페이지 열기
              </a>
            </div>

            <label>
              <span>포스트 유형</span>
              <select value={postType} onChange={(event) => setPostType(event.target.value)}>
                <option value="기술 블로그">기술 블로그</option>
                <option value="프로젝트 회고">프로젝트 회고</option>
                <option value="구현 과정 설명">구현 과정 설명</option>
                <option value="코드 리뷰 정리">코드 리뷰 정리</option>
              </select>
            </label>

            <button type="submit" disabled={!canSubmit}>
              {isLoading ? "생성 중..." : "초안 생성"}
            </button>

            {error && <p className="error-message">{error}</p>}
          </form>

          <section className="output-panel" aria-live="polite">
            <div className="output-header">
              <h2>생성 결과</h2>
              <button type="button" onClick={handleCopy} disabled={!result}>
                복사
              </button>
            </div>
            <div className="result-box">
              {isLoading && <p className="muted">OpenAI가 저장소 내용을 정리하는 중입니다.</p>}
              {!isLoading && !result && !error && (
                <p className="muted">생성된 블로그 초안이 여기에 표시됩니다.</p>
              )}
              {result && <pre>{result}</pre>}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
