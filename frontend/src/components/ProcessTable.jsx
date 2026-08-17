export default function ProcessTable({ processes }) {
  if (!processes || processes.length === 0) return null;
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "12px", padding: "20px", overflow: "hidden"
    }}>
      <div style={{ fontWeight: 600, marginBottom: "16px", fontSize: "14px" }}>🔄 Top Processes</div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "12px" }}>
          <thead>
            <tr style={{ color: "var(--muted)", textAlign: "left" }}>
              {["PID", "Name", "CPU%", "RAM%", "Status"].map(h => (
                <th key={h} style={{ padding: "6px 8px",
                  borderBottom: "1px solid var(--border)", fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {processes.slice(0, 8).map((p, i) => (
              <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}
                onMouseEnter={e => e.currentTarget.style.background = "var(--border)"}
                onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
                <td className="mono" style={{ padding: "7px 8px",
                  color: "var(--muted)" }}>{p.pid}</td>
                <td style={{ padding: "7px 8px", maxWidth: "140px",
                  overflow: "hidden", textOverflow: "ellipsis",
                  whiteSpace: "nowrap" }}>{p.name}</td>
                <td className="mono" style={{ padding: "7px 8px",
                  color: p.cpu_percent > 10 ? "var(--yellow)" : "var(--text)" }}>
                  {(p.cpu_percent || 0).toFixed(1)}%
                </td>
                <td className="mono" style={{ padding: "7px 8px" }}>
                  {(p.memory_percent || 0).toFixed(1)}%
                </td>
                <td style={{ padding: "7px 8px" }}>
                  <span style={{
                    fontSize: "10px", padding: "2px 6px", borderRadius: "10px",
                    background: p.status === "running" ? "#052e16" : "var(--border)",
                    color: p.status === "running" ? "var(--green)" : "var(--muted)"
                  }}>{p.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
