function GaugeRing({ percent, color }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const fill = ((percent || 0) / 100) * circ;
  return (
    <svg width="90" height="90" viewBox="0 0 90 90">
      <circle cx="45" cy="45" r={r} fill="none" stroke="var(--border)" strokeWidth="8" />
      <circle cx="45" cy="45" r={r} fill="none" stroke={color} strokeWidth="8"
        strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
        transform="rotate(-90 45 45)"
        style={{ transition: "stroke-dasharray 0.5s ease" }} />
      <text x="45" y="50" textAnchor="middle" fill="white" fontSize="14" fontWeight="600"
        fontFamily="JetBrains Mono, monospace">
        {Math.round(percent || 0)}%
      </text>
    </svg>
  );
}
export default function MetricCard({ title, percent, details, color, icon }) {
  const getColor = (p) => {
    if (p > 85) return "var(--red)";
    if (p > 65) return "var(--yellow)";
    return color || "var(--green)";
  };
  const c = getColor(percent);
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "12px", padding: "20px", display: "flex",
      gap: "16px", alignItems: "center", flex: 1, minWidth: "220px"
    }}>
      <GaugeRing percent={percent} color={c} />
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "8px" }}>
          <span>{icon}</span>
          <span style={{ fontWeight: 600, fontSize: "14px" }}>{title}</span>
        </div>
        {details.map((d, i) => (
          <div key={i} style={{
            display: "flex", justifyContent: "space-between",
            fontSize: "12px", color: "var(--muted)", marginBottom: "3px"
          }}>
            <span>{d.label}</span>
            <span className="mono" style={{ color: "var(--text)" }}>{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
