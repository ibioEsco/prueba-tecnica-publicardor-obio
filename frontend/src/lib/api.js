// URL del backend. Se define por entorno en .env.development / .env.production
// (ver frontend/.env.example). Se quita la barra final para no generar "//generate".
export const BASE = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/+$/, "");

export async function generatePost(topic, language) {
  const res = await fetch(`${BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, language }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchPosts() {
  const res = await fetch(`${BASE}/posts`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updatePost(id, status, text) {
  const res = await fetch(`${BASE}/posts/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function regenerateImage(id, imagePrompt) {
  const res = await fetch(`${BASE}/posts/${id}/regenerate-image`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_prompt: imagePrompt || null }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function publishPost(id) {
  const res = await fetch(`${BASE}/posts/${id}/publish`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
