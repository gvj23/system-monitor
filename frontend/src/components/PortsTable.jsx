export default function PortsTable({ ports }) {
  if (!ports || ports.length === 0) return null;
  const listening = ports.filter(p => p.status === "LISTEN");
  const established = ports.filter(p => p.status === "ESTABLISHED");
  const statusColor = (s) => {
    if (s === "LISTEN") return "var(--blue)";
    if (s === "ESTABLISHED") return "var(--green)";
    return "var(--muted)";
  };
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "12px", padding: "20px", overflow: "hidden"
    }}>
      <div style={{ fontWeight: 600, marginBottom: "8px", fontSize: "14px" }}>🌐 Open Ports</div>
      <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
        <span style={{ fontSize: "11px", color: "var(--blue)" }}>👂 {listening.length} Listening</span>
        <span style={{ fontSize: "11px", color: "var(--green)" }}>🔗 {established.length} Established</span>
      </div>
      <div style={{ overflowX: "auto", maxHeight: "260px", overflowY: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "11px" }}>
          <thead style={{ position: "sticky", top: 0, background: "var(--surface)" }}>
            <tr style={{ color: "var(--muted)" }}>
              {["Proto", "Local", "Remote", "Status"].map(h => (
                <th key={h} style={{ padding: "5px 8px",
                  borderBottom: "1px solid var(--border)",
                  textAlign: "left", fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ports.slice(0, 20).map((p, i) => (
              <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                <td className="mono" style={{ padding: "5px 8px",
                  color: p.proto === "TCP" ? "var(--blue)" : "var(--purple)" }}>{p.proto}</td>
                <td className="mono" style={{ padding: "5px 8px", fontSize: "10px" }}>{p.local}</td>
                <td className="mono" style={{ padding: "5px 8px",
                  color: "var(--muted)", fontSize: "10px" }}>{p.remote}</td>
                <td style={{ padding: "5px 8px" }}>
                  <span style={{
                    fontSize: "9px", padding: "2px 5px", borderRadius: "8px",
                    border: `1px solid ${statusColor(p.status)}`,
                    color: statusColor(p.status)
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
