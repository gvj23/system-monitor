export default function CPUCoreChart({ cores }) {
  if (!cores || cores.length === 0) return null;
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "12px", padding: "20px"
    }}>
      <div style={{ fontWeight: 600, marginBottom: "16px", fontSize: "14px" }}>
        ⚙️ Per Core Usage
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {cores.map((c) => {
          const pct = c.usage || 0;
          const color = pct > 85 ? "var(--red)" : pct > 65 ? "var(--yellow)" : "var(--green)";
          return (
            <div key={c.core} style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <span className="mono" style={{ fontSize: "11px", color: "var(--muted)", width: "48px" }}>
                Core {c.core}
              </span>
              <div style={{ flex: 1, background: "var(--border)", borderRadius: "4px", height: "8px", overflow: "hidden" }}>
                <div style={{
                  width: `${pct}%`, height: "100%", background: color,
                  borderRadius: "4px", transition: "width 0.5s ease"
                }} />
              </div>
              <span className="mono" style={{ fontSize: "11px", width: "38px", textAlign: "right", color }}>
                {pct.toFixed(1)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
