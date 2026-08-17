export default function Header({ data, agentStatus }) {
  const isOnline = agentStatus === "online";
  const sys = data?.system;
  const uptime = data?.uptime;
  return (
    <div style={{
      background: "var(--surface)", borderBottom: "1px solid var(--border)",
      padding: "16px 24px", display: "flex", alignItems: "center",
      justifyContent: "space-between", flexWrap: "wrap", gap: "12px"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{ fontSize: "20px" }}>🖥</span>
        <div>
          <div style={{ fontWeight: 600, fontSize: "16px" }}>System Monitor</div>
          <div className="mono" style={{ fontSize: "12px", color: "var(--muted)" }}>
            {sys?.hostname || "—"} · {sys?.os || "—"} · {sys?.architecture || "—"}
          </div>
        </div>
      </div>
      <div style={{ display: "flex", gap: "24px", alignItems: "center" }}>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "12px", color: "var(--muted)" }}>Uptime</div>
          <div className="mono" style={{ fontSize: "13px" }}>{uptime?.uptime_string || "—"}</div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: "12px", color: "var(--muted)" }}>Last seen</div>
          <div className="mono" style={{ fontSize: "13px" }}>{data?.timestamp?.split(" ")[1] || "—"}</div>
        </div>
        <div style={{
          display: "flex", alignItems: "center", gap: "6px",
          background: isOnline ? "#052e16" : "#1f1115",
          border: `1px solid ${isOnline ? "var(--green)" : "var(--red)"}`,
          borderRadius: "20px", padding: "4px 12px", fontSize: "13px",
          color: isOnline ? "var(--green)" : "var(--red)", fontWeight: 600
        }}>
          <span style={{
            width: "8px", height: "8px", borderRadius: "50%",
            background: isOnline ? "var(--green)" : "var(--red)",
            animation: isOnline ? "pulse 2s infinite" : "none"
          }} />
          {isOnline ? "Online" : "Offline"}
        </div>
      </div>
      <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }`}</style>
    </div>
  );
}
