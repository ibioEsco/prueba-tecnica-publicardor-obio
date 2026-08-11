const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

export async function publishPost(id) {
  const res = await fetch(`${BASE}/posts/${id}/publish`, { method: "POST" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
