import { useState, useEffect, useCallback } from "react";
import PostCard from "./components/PostCard";
import History from "./components/History";
import { generatePost, fetchPosts } from "./lib/api";

export default function App() {
  const [topic, setTopic] = useState("");
  const [language, setLanguage] = useState("en");
  const [posts, setPosts] = useState([]);
  const [activePost, setActivePost] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadPosts = useCallback(async () => {
    try { const data = await fetchPosts(); setPosts(data); } catch {}
  }, []);

  useEffect(() => { loadPosts(); }, [loadPosts]);

  async function handleGenerate(e) {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true); setError(null);
    try {
      const post = await generatePost(topic.trim(), language);
      setPosts(prev => [post, ...prev]);
      setActivePost(post);
      setTopic("");
    } catch (err) { setError(err.message); }
    setLoading(false);
  }

  function handlePostUpdate(updated) {
    setPosts(prev => prev.map(p => p.id === updated.id ? updated : p));
    if (activePost?.id === updated.id) setActivePost(updated);
  }

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <header style={{
        borderBottom: "1px solid var(--border)", background: "var(--surface)",
        padding: "0 2rem", display: "flex", alignItems: "center", gap: "1rem", height: 56,
      }}>
        <span style={{ fontFamily: "monospace", fontSize: "0.8rem", color: "var(--green)", letterSpacing: "0.1em" }}>
          ▶ COBOL_ENGINE
        </span>
        <span style={{ color: "var(--text-dim)", fontSize: "0.75rem" }}>v0.1.0</span>
        <div style={{ marginLeft: "auto", fontSize: "0.75rem", color: "var(--text-muted)" }}>
          LinkedIn content engine · Juan Lucas Barbier
        </div>
      </header>

      <main style={{ maxWidth: 1100, margin: "0 auto", padding: "2rem" }}>
        {/* Generator form */}
        <div style={{
          background: "var(--surface)", border: "1px solid var(--border)",
          borderRadius: "var(--radius-lg)", padding: "1.5rem", marginBottom: "1.5rem",
        }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "1rem" }}>
            Generate post
          </div>
          <form onSubmit={handleGenerate} style={{ display: "flex", gap: "0.75rem", alignItems: "flex-end" }}>
            <input
              value={topic} onChange={e => setTopic(e.target.value)}
              placeholder="Topic — e.g. 'COBOL retirement knowledge transfer' or 'IBM z16 pricing'"
              style={{ flex: 1, padding: "0.75rem 1rem" }} disabled={loading}
            />
            <select value={language} onChange={e => setLanguage(e.target.value)}
              style={{ padding: "0.75rem 0.875rem", minWidth: 90 }} disabled={loading}>
              <option value="en">EN</option>
              <option value="es">ES</option>
            </select>
            <button type="submit" disabled={loading || !topic.trim()} style={{
              padding: "0.75rem 1.5rem",
              background: loading ? "var(--surface-2)" : "var(--green-bg)",
              border: "1px solid", borderColor: loading ? "var(--border)" : "var(--green-dim)",
              color: loading ? "var(--text-muted)" : "var(--green)",
              fontWeight: 600, minWidth: 120,
            }}>
              {loading ? "Generating…" : "Generate →"}
            </button>
          </form>
          {error && (
            <div style={{ marginTop: "0.75rem", padding: "0.75rem", background: "var(--red-bg)",
              border: "1px solid #ef444430", borderRadius: "var(--radius)", fontSize: "0.8125rem", color: "var(--red)" }}>
              {error}
            </div>
          )}
          {loading && (
            <div style={{ marginTop: "0.875rem", fontSize: "0.8125rem", color: "var(--text-muted)" }}>
              <span style={{ color: "var(--green-dim)" }}>▶</span> Generating post · scoring virality · building image…
            </div>
          )}
        </div>

        {/* Active post */}
        {activePost && (
          <div style={{ marginBottom: "1.5rem" }}>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.75rem" }}>
              Current post
            </div>
            <PostCard post={activePost} onUpdate={handlePostUpdate} />
          </div>
        )}

        {/* History */}
        {posts.length > 0 && (
          <div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.75rem" }}>
              All posts ({posts.length})
            </div>
            <History posts={posts} onSelect={setActivePost} selectedId={activePost?.id} />
          </div>
        )}

        {posts.length === 0 && !loading && (
          <div style={{ textAlign: "center", padding: "3rem", color: "var(--text-dim)", fontSize: "0.875rem" }}>
            <div style={{ fontFamily: "monospace", fontSize: "2rem", color: "var(--border-hover)", marginBottom: "0.75rem" }}>{">_"}</div>
            No posts yet. Enter a topic to generate your first post.
          </div>
        )}
      </main>
    </div>
  );
}
