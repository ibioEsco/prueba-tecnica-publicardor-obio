const CONFIG = {
  draft:     { label: "Draft",     color: "#888884", bg: "rgba(136,136,132,0.1)" },
  approved:  { label: "Approved",  color: "#00cc33", bg: "rgba(0,204,51,0.1)" },
  discarded: { label: "Discarded", color: "#ef4444", bg: "rgba(239,68,68,0.1)" },
  published: { label: "Published", color: "#00ff41", bg: "rgba(0,255,65,0.12)" },
  simulated: { label: "Simulated", color: "#f59e0b", bg: "rgba(245,158,11,0.1)" },
};

export default function StatusBadge({ status }) {
  const cfg = CONFIG[status] || CONFIG.draft;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "0.35rem",
      padding: "0.2rem 0.6rem",
      borderRadius: "99px",
      fontSize: "0.75rem", fontWeight: 600, letterSpacing: "0.04em", textTransform: "uppercase",
      color: cfg.color, background: cfg.bg,
      border: `1px solid ${cfg.color}30`,
    }}>
      {status === "simulated" && (
        <span style={{ fontSize: "0.65rem" }}>⚠</span>
      )}
      {cfg.label}
    </span>
  );
}
