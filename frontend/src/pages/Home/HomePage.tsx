import { useEffect, useState } from "react";
import { fetchHealth } from "@/api/client";

export function HomePage() {
  const [status, setStatus] = useState<string>("로딩…");
  const [detail, setDetail] = useState<string>("");

  useEffect(() => {
    fetchHealth()
      .then((body) => {
        setStatus("연결됨");
        setDetail(JSON.stringify(body, null, 2));
      })
      .catch((e: Error) => {
        setStatus("실패");
        setDetail(e.message);
      });
  }, []);

  return (
    <main style={{ padding: "2rem", maxWidth: 640 }}>
      <h1>청년 위험군 · 자격증 로드맵</h1>
      <p>백엔드 헬스: {status}</p>
      <pre
        style={{
          background: "#1e293b",
          color: "#e2e8f0",
          padding: "1rem",
          borderRadius: 8,
          overflow: "auto",
        }}
      >
        {detail}
      </pre>
      <p style={{ fontSize: "0.875rem", color: "#64748b" }}>
        로컬 개발: 터미널에서 FastAPI(uvicorn)와 <code>npm run dev</code>를 동시에 실행하세요.
        프록시는 <code>/api</code> → 8000 입니다.
      </p>
    </main>
  );
}
