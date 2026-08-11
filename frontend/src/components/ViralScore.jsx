export default function ViralScore({ score, reasons }) {
  const color = score >= 70 ? "#00ff41" : score >= 45 ? "#f59e0b" : "#ef4444";
  const label = score >= 70 ? "High potential" : score >= 45 ? "Publish with edits" : "Needs work";

  return (
    <div style={{
      background: "var(--surface-2)",
      border: "1px solid var(--border)",
      borderRadius: "var(--radius-lg)",
      padding: "1rem 1.25rem",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginBottom: "0.875rem" }}>
        <div style={{
          fontSize: "2rem", fontWeight: 700, color,
          fontVariantNumeric: "tabular-nums", lineHeight: 1,
        }}>
          {score}
        </div>
        <div>
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Viral score</div>
          <div style={{ fontSize: "0.8125rem", color, fontWeight: 500 }}>{label}</div>
        </div>
        <div style={{ marginLeft: "auto", width: 48, height: 48 }}>
          <svg viewBox="0 0 48 48" style={{ transform: "rotate(-90deg)" }}>
            <circle cx="24" cy="24" r="20" fill="none" stroke="var(--border)" strokeWidth="4"/>
            <circle
              cx="24" cy="24" r="20" fill="none"
              stroke={color} strokeWidth="4"
              strokeDasharray={`${(score / 100) * 125.66} 125.66`}
              strokeLinecap="round"
            />
          </svg>
        </div>
      </div>

      {/* Bar */}
      <div style={{ height: 4, background: "var(--border)", borderRadius: 2, marginBottom: "1rem" }}>
        <div style={{ height: "100%", width: `${score}%`, background: color, borderRadius: 2, transition: "width 0.5s ease" }}/>
      </div>

      {/* Reasons */}
      <div style={{ display: "flex", flexDirection: "column", gap: "0.375rem" }}>
        {reasons.map((r, i) => {
          const isGood = r.startsWith("✓");
          const isMid = r.startsWith("~");
          const reasonColor = isGood ? "var(--green-dim)" : isMid ? "var(--amber)" : "var(--red)";
          return (
            <div key={i} style={{ fontSize: "0.8125rem", color: reasonColor, lineHeight: 1.4 }}>
              {r}
            </div>
          );
        })}
      </div>
    </div>
  );
}
