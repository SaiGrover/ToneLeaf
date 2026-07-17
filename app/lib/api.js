const configuredApi = process.env.NEXT_PUBLIC_TONELEAF_API;
const LOCAL_API = configuredApi === "same-origin"
  ? ""
  : (configuredApi || "http://127.0.0.1:8765").replace(/\/$/, "");

export async function analyzeLocally(text, mode) {
  const response = await fetch(`${LOCAL_API}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, mode }),
    cache: "no-store",
    credentials: "omit",
    referrerPolicy: "no-referrer",
  });
  if (!response.ok) throw new Error(`Local analysis failed (${response.status})`);
  return response.json();
}
