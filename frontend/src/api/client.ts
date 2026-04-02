/**
 * API 베이스 URL.
 * 로컬: Vite proxy로 같은 오리진에서 /api 호출 가능.
 * Vercel 등: VITE_API_BASE_URL=https://your-api.railway.app
 */
export function getApiBase(): string {
  const env = import.meta.env.VITE_API_BASE_URL;
  if (env && env.length > 0) return env.replace(/\/$/, "");
  return "";
}

export async function fetchHealth(): Promise<unknown> {
  const base = getApiBase();
  const url = base ? `${base}/api/v1/health` : "/api/v1/health";
  const res = await fetch(url);
  if (!res.ok) throw new Error(`health ${res.status}`);
  return res.json();
}
