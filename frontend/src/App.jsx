import React, { useMemo, useState } from "react";

const contacts = [
  {
    id: 1,
    name: "홍길동",
    phone: "010-1234-5678",
    relation: "가족",
    avatar: "홍"
  },
  {
    id: 2,
    name: "김민수",
    phone: "010-2345-6789",
    relation: "친구",
    avatar: "김"
  },
  {
    id: 3,
    name: "이영희",
    phone: "010-3456-7890",
    relation: "동료",
    avatar: "이"
  },
  {
    id: 4,
    name: "박지성",
    phone: "010-4567-8901",
    relation: "가족",
    avatar: "박"
  }
];

function Header({ title, onBack, action }) {
  return (
    <header className="top-bar">
      <button className="icon-button" type="button" onClick={onBack} aria-label="뒤로 가기">
        <span aria-hidden="true">‹</span>
      </button>
      <strong>{title}</strong>
      <button className="icon-button" type="button" aria-label={action || "추가"}>
        <span aria-hidden="true">+</span>
      </button>
    </header>
  );
}

function BottomNav({ active }) {
  const items = [
    { id: "home", label: "Home", icon: "⌂" },
    { id: "history", label: "History", icon: "▤" },
    { id: "settings", label: "Settings", icon: "⚙" }
  ];

  return (
    <nav className="bottom-nav" aria-label="하단 메뉴">
      {items.map((item) => (
        <button className={active === item.id ? "active" : ""} key={item.id} type="button">
          <span aria-hidden="true">{item.icon}</span>
          {item.label}
        </button>
      ))}
    </nav>
  );
}

function LocationArt() {
  return (
    <div className="location-art" aria-hidden="true">
      <div className="art-card">
        <div className="map-tile">
          <span className="map-route route-a" />
          <span className="map-route route-b" />
          <span className="pin-main" />
          <span className="mini-face face-one" />
          <span className="mini-face face-two" />
          <span className="spark spark-one" />
          <span className="spark spark-two" />
          <span className="heart heart-one" />
          <span className="heart heart-two" />
        </div>
      </div>
    </div>
  );
}

function ContactRow({ contact, selected, onSelect, compact = false }) {
  return (
    <button
      className={`contact-row ${selected ? "selected" : ""} ${compact ? "compact" : ""}`}
      type="button"
      onClick={() => onSelect(contact)}
    >
      <span className="avatar">{contact.avatar}</span>
      <span className="contact-copy">
        <strong>{contact.name}</strong>
        <small>{contact.phone}</small>
      </span>
      <span className="select-dot" aria-hidden="true">
        {selected ? "✓" : ""}
      </span>
    </button>
  );
}

function HomePage({ selectedContact, onSelectFlow, onEmergency }) {
  return (
    <div className="screen-content home-screen">
      <LocationArt />
      <section className="intro-copy">
        <h1>내 위치 전송</h1>
        <p>등록된 연락처로 현재 위치를 문자로 전송합니다.</p>
        <span className="status-pill">등록된 연락처: {contacts.length}명</span>
      </section>

      <div className="action-stack">
        <button className="primary-button" type="button" onClick={onSelectFlow}>
          현재 위치 문자 전송
        </button>
        <button className="outline-danger" type="button" onClick={onEmergency}>
          현재 위치 긴급 문자 전송
        </button>
      </div>

      <section className="recipient-preview">
        <div className="section-title">
          <span>전송 대상</span>
          <button type="button" onClick={onSelectFlow} aria-label="전송 대상 변경">
            ›
          </button>
        </div>
        <ContactRow contact={selectedContact} selected compact onSelect={onSelectFlow} />
      </section>
    </div>
  );
}

function SelectPage({ selectedContact, setSelectedContact, onCancel, onNext }) {
  const [query, setQuery] = useState("");
  const filteredContacts = useMemo(
    () => contacts.filter((contact) => `${contact.name} ${contact.phone}`.includes(query.trim())),
    [query]
  );

  return (
    <div className="screen-content select-screen">
      <div className="search-field">
        <span aria-hidden="true">⌕</span>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="이름 또는 번호 검색"
          type="search"
        />
      </div>

      <div className="section-title list-heading">
        <span>등록된 연락처</span>
        <strong>총 {contacts.length}명</strong>
      </div>

      <div className="contact-list">
        {filteredContacts.map((contact) => (
          <ContactRow
            contact={contact}
            key={contact.id}
            onSelect={setSelectedContact}
            selected={selectedContact.id === contact.id}
          />
        ))}
      </div>

      <div className="sticky-actions">
        <button className="primary-button" type="button" onClick={onNext}>
          선택한 대상에게 전송 (1)
        </button>
        <button className="ghost-button" type="button" onClick={onCancel}>
          취소
        </button>
      </div>
    </div>
  );
}

function MapPreview() {
  return (
    <div className="map-preview" aria-label="현재 위치 지도">
      <div className="grid-map">
        <span className="road road-main" />
        <span className="road road-cross" />
        <span className="road road-diagonal" />
        <span className="water" />
        <span className="park park-one" />
        <span className="park park-two" />
        <span className="map-pin" />
      </div>
      <div className="location-caption">
        <span className="caption-icon">⌖</span>
        <div>
          <strong>현재 위치: 서울특별시 강남구</strong>
          <small>테헤란로 인근, 정확도 높음</small>
        </div>
      </div>
    </div>
  );
}

function ConfirmPage({ selectedContact, onSend, onCancel }) {
  return (
    <div className="screen-content confirm-screen">
      <MapPreview />
      <section className="confirm-copy">
        <h1>현재 위치를 전송합니다</h1>
      </section>
      <ContactRow contact={selectedContact} selected compact onSelect={() => {}} />
      <div className="sticky-actions confirm-actions">
        <button className="primary-button" type="button" onClick={onSend}>
          전송
        </button>
        <button className="text-button" type="button" onClick={onCancel}>
          취소
        </button>
      </div>
    </div>
  );
}

function SuccessPage({ selectedContact, onDone, onHistory }) {
  return (
    <div className="screen-content success-screen">
      <div className="success-mark" aria-hidden="true">
        ✓
      </div>
      <section className="success-copy">
        <h1>위치 전송 완료!</h1>
        <p>
          {selectedContact.name}님({selectedContact.phone})에게 현재 위치가 성공적으로 전송되었습니다.
        </p>
      </section>
      <div className="sticky-actions success-actions">
        <button className="primary-button" type="button" onClick={onDone}>
          확인
        </button>
        <button className="ghost-button" type="button" onClick={onHistory}>
          전송 내역 보기
        </button>
      </div>
    </div>
  );
}
>>>>>>> Stashed changes

export default function App() {
  const [page, setPage] = useState("home");
  const [selectedContact, setSelectedContact] = useState(contacts[0]);

  const titles = {
    home: "위치 전송 메인",
    select: "전송 대상 선택",
    confirm: "위치 전송 확인",
    success: "전송 상태 및 완료"
  };

<<<<<<< Updated upstream
  async function readResponse(response) {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }

    const text = await response.text();
    return { detail: text || "서버에서 비어 있는 응답을 받았습니다." };
  }

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

      const data = await readResponse(response);

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
=======
  const goHome = () => setPage("home");

  return (
    <main className="app-shell">
      <section className="device-frame" aria-label="위치 공유 앱 미리보기">
        <Header title={titles[page]} onBack={page === "home" ? goHome : () => setPage("home")} />
>>>>>>> Stashed changes

        {page === "home" && (
          <HomePage
            selectedContact={selectedContact}
            onSelectFlow={() => setPage("select")}
            onEmergency={() => setPage("confirm")}
          />
        )}

        {page === "select" && (
          <SelectPage
            selectedContact={selectedContact}
            setSelectedContact={setSelectedContact}
            onCancel={goHome}
            onNext={() => setPage("confirm")}
          />
        )}

        {page === "confirm" && (
          <ConfirmPage selectedContact={selectedContact} onCancel={goHome} onSend={() => setPage("success")} />
        )}

        {page === "success" && (
          <SuccessPage selectedContact={selectedContact} onDone={goHome} onHistory={() => setPage("home")} />
        )}

<<<<<<< Updated upstream
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
=======
        <BottomNav active={page === "success" ? "history" : "home"} />
>>>>>>> Stashed changes
      </section>

      <aside className="page-switcher" aria-label="화면 바로가기">
        {Object.entries(titles).map(([id, title]) => (
          <button className={page === id ? "current" : ""} key={id} type="button" onClick={() => setPage(id)}>
            {title}
          </button>
        ))}
      </aside>
    </main>
  );
}
