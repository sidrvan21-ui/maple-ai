"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const ROLES = [
  "product",
  "finance",
  "engineering",
  "exec",
  "growth",
  "legal",
] as const;

export default function HomePage() {
  const [health, setHealth] = useState<string>("checking…");
  const [role, setRole] = useState<(typeof ROLES)[number]>("product");
  const [me, setMe] = useState<string>("not signed in");

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => r.json())
      .then((j) => setHealth(j.status ?? "unknown"))
      .catch(() => setHealth("down — start the API on :8000"));
  }, []);

  async function signIn() {
    const res = await fetch(`${API}/api/auth/dev-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Siddharth", role }),
    });
    const data = await res.json();
    localStorage.setItem("maple_token", data.access_token);
    const meRes = await fetch(`${API}/api/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    const principal = await meRes.json();
    setMe(`${principal.name} · ${principal.role}`);
  }

  return (
    <main style={{ maxWidth: 640, margin: "4rem auto", padding: "0 1.5rem" }}>
      <p style={{ letterSpacing: "0.08em", fontSize: "0.8rem" }}>MAPLE AI</p>
      <h1 style={{ fontWeight: 500, fontSize: "2.2rem" }}>
        Phase-gate workbench
      </h1>
      <p>
        Part 1 scaffold. Kitchen (API) and dining room (this page) are separate.
        Gates and agentic RAG come later.
      </p>
      <p>
        API health: <strong>{health}</strong>
      </p>
      <label>
        Sign in as{" "}
        <select
          value={role}
          onChange={(e) =>
            setRole(e.target.value as (typeof ROLES)[number])
          }
        >
          {ROLES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </label>{" "}
      <button type="button" onClick={signIn}>
        Dev login
      </button>
      <p>Session: {me}</p>
    </main>
  );
}
