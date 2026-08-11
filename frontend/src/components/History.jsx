import StatusBadge from "./StatusBadge";

export default function History({ posts, onSelect, selectedId }) {
  if (!posts.length) return null;

  return (
    <div style={{
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-lg)",
      overflow: "hidden",
    }}>
      <div style={{
        padding: "0.75rem 1.25rem",
        borderBottom: "1px solid var(--border)",
        background: "var(--surface-2)",
        fontSize: "0.8125rem", fontWeight: 600, color: "var(--text-muted)",
        textTransform: "uppercase", letterSpacing: "0.05em",
      }}>
        Content history
      </div>
      <div>
        {posts.map((post, i) => (
          <div
            key={post.id}
            onClick={() => onSelect(post)}
            style={{
              padding: "0.875rem 1.25rem",
              borderBottom: i < posts.length - 1 ? "1px solid var(--border)" : "none",
              cursor: "pointer",
              background: selectedId === post.id ? "var(--surface-2)" : "transparent",
              transition: "background 0.1s",
              display: "grid",
              gridTemplateColumns: "1fr auto auto auto",
              alignItems: "center",
              gap: "1rem",
            }}
            onMouseEnter={e => { if (selectedId !== post.id) e.currentTarget.style.background = "rgba(255,255,255,0.02)"; }}
            onMouseLeave={e => { if (selectedId !== post.id) e.currentTarget.style.background = "transparent"; }}
          >
            <div>
              <div style={{ fontSize: "0.875rem", color: "var(--text)" }}>{post.topic}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                {post.language.toUpperCase()} · {new Date(post.created_at).toLocaleString()}
              </div>
            </div>
            <div style={{
              fontSize: "0.8125rem", fontWeight: 700,
              color: post.viral_score >= 70 ? "var(--green)" : post.viral_score >= 45 ? "var(--amber)" : "var(--red)",
            }}>
              {post.viral_score}
            </div>
            <StatusBadge status={post.status} />
            <div style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>→</div>
          </div>
        ))}
      </div>
    </div>
  );
}
