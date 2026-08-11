import { useState } from "react";
import ViralScore from "./ViralScore";
import StatusBadge from "./StatusBadge";
import { updatePost, publishPost } from "../lib/api";

const btnBase = {
  padding: "0.5rem 1rem",
  borderRadius: "var(--radius)",
  fontSize: "0.8125rem",
  fontWeight: 500,
  cursor: "pointer",
  border: "1px solid",
  transition: "all 0.15s",
};

export default function PostCard({ post: initialPost, onUpdate }) {
  const [post, setPost] = useState(initialPost);
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(initialPost.text);
  const [loading, setLoading] = useState(null);
  const [publishResult, setPublishResult] = useState(null);

  const isTerminal = ["published", "discarded"].includes(post.status);

  async function handleAction(action) {
    setLoading(action);
    try {
      let updated;
      if (action === "approve") {
        updated = await updatePost(post.id, "approved");
      } else if (action === "discard") {
        updated = await updatePost(post.id, "discarded");
      } else if (action === "save-edit") {
        updated = await updatePost(post.id, post.status, editText);
        setEditing(false);
      } else if (action === "publish") {
        const result = await publishPost(post.id);
        setPublishResult(result);
        updated = { ...post, status: result.status };
      }
      if (updated) {
        setPost(updated);
        onUpdate?.(updated);
      }
    } catch (e) {
      alert(e.message);
    }
    setLoading(null);
  }

  return (
    <div style={{
      background: "var(--surface)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-lg)",
      overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{
        padding: "0.875rem 1.25rem",
        borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", gap: "0.75rem",
        background: "var(--surface-2)",
      }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.2rem" }}>
            {post.language === "es" ? "ES" : "EN"} · {new Date(post.created_at).toLocaleDateString()}
          </div>
          <div style={{ fontSize: "0.875rem", fontWeight: 500, color: "var(--text)" }}>
            {post.topic}
          </div>
        </div>
        <StatusBadge status={post.status} />
      </div>

      {/* Body */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 280px", gap: 0 }}>

        {/* Left: post text + actions */}
        <div style={{ padding: "1.25rem", borderRight: "1px solid var(--border)" }}>
          {/* Post preview header */}
          <div style={{
            display: "flex", alignItems: "center", gap: "0.5rem",
            marginBottom: "0.875rem",
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: "50%",
              background: "linear-gradient(135deg, #1e3a5f, #00cc33)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "0.75rem", fontWeight: 700, color: "#fff",
            }}>JLB</div>
            <div>
              <div style={{ fontSize: "0.8125rem", fontWeight: 600 }}>Juan Lucas Barbier</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Principal Architect · Mainframe & Legacy Systems</div>
            </div>
          </div>

          {editing ? (
            <textarea
              value={editText}
              onChange={e => setEditText(e.target.value)}
              rows={10}
              style={{
                width: "100%", padding: "0.875rem",
                resize: "vertical", lineHeight: 1.7,
                fontSize: "0.9rem",
              }}
            />
          ) : (
            <div style={{
              fontSize: "0.9rem", lineHeight: 1.75, color: "var(--text)",
              whiteSpace: "pre-wrap",
            }}>
              {post.text}
            </div>
          )}

          {/* Actions */}
          {!isTerminal && (
            <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem", flexWrap: "wrap" }}>
              {editing ? (
                <>
                  <button
                    onClick={() => handleAction("save-edit")}
                    disabled={loading === "save-edit"}
                    style={{ ...btnBase, background: "var(--green-bg)", borderColor: "var(--green-dim)", color: "var(--green)" }}
                  >
                    {loading === "save-edit" ? "Saving…" : "Save edits"}
                  </button>
                  <button
                    onClick={() => { setEditing(false); setEditText(post.text); }}
                    style={{ ...btnBase, background: "transparent", borderColor: "var(--border)", color: "var(--text-muted)" }}
                  >Cancel</button>
                </>
              ) : (
                <>
                  {post.status !== "approved" && (
                    <button
                      onClick={() => handleAction("approve")}
                      disabled={!!loading}
                      style={{ ...btnBase, background: "var(--green-bg)", borderColor: "var(--green-dim)", color: "var(--green)" }}
                    >
                      {loading === "approve" ? "Approving…" : "✓ Approve"}
                    </button>
                  )}
                  {post.status === "approved" && (
                    <button
                      onClick={() => handleAction("publish")}
                      disabled={!!loading}
                      style={{ ...btnBase, background: "#1e3a5f", borderColor: "#3b82f6", color: "#60a5fa" }}
                    >
                      {loading === "publish" ? "Publishing…" : "↑ Publish to LinkedIn"}
                    </button>
                  )}
                  <button
                    onClick={() => setEditing(true)}
                    style={{ ...btnBase, background: "transparent", borderColor: "var(--border)", color: "var(--text-muted)" }}
                  >✎ Edit</button>
                  <button
                    onClick={() => handleAction("discard")}
                    disabled={!!loading}
                    style={{ ...btnBase, background: "var(--red-bg)", borderColor: "#ef444440", color: "var(--red)" }}
                  >
                    {loading === "discard" ? "…" : "✕ Discard"}
                  </button>
                </>
              )}
            </div>
          )}

          {/* Publish result */}
          {publishResult && (
            <div style={{
              marginTop: "1rem",
              padding: "0.875rem",
              background: publishResult.simulated ? "var(--amber-bg)" : "var(--green-bg)",
              border: `1px solid ${publishResult.simulated ? "#f59e0b30" : "#00ff4130"}`,
              borderRadius: "var(--radius)",
              fontSize: "0.8125rem",
            }}>
              {publishResult.simulated ? (
                <>
                  <div style={{ color: "var(--amber)", fontWeight: 600, marginBottom: "0.5rem" }}>
                    ⚠ Simulated publication — not posted to LinkedIn
                  </div>
                  <div style={{ color: "var(--text-muted)", marginBottom: "0.75rem" }}>
                    {publishResult.setup_instructions}
                  </div>
                  <details>
                    <summary style={{ color: "var(--text-muted)", cursor: "pointer", marginBottom: "0.5rem" }}>
                      API payload preview
                    </summary>
                    <pre style={{ fontSize: "0.75rem", color: "var(--text-dim)", overflow: "auto" }}>
                      {JSON.stringify(publishResult.payload_preview, null, 2)}
                    </pre>
                  </details>
                </>
              ) : (
                <div style={{ color: "var(--green)" }}>
                  ✓ Published to LinkedIn — <a href={publishResult.post_url} target="_blank" rel="noopener noreferrer" style={{ color: "var(--blue)" }}>view post</a>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: image + score */}
        <div style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
          {post.image_url && (
            <div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.5rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Image
              </div>
              <img
                src={post.image_url}
                alt="Post visual"
                style={{ width: "100%", borderRadius: "var(--radius)", border: "1px solid var(--border)", display: "block" }}
              />
              <div style={{ fontSize: "0.7rem", color: "var(--text-dim)", marginTop: "0.375rem", lineHeight: 1.4 }}>
                {post.image_prompt}
              </div>
            </div>
          )}
          <ViralScore score={post.viral_score} reasons={post.viral_reasons} />
        </div>
      </div>
    </div>
  );
}
