export default function SecurityPanel({ security }) {
  if (!security) return null;

  const {
    logged_in_users = [],
    sudo_usage = [],
    ssh_inbound_success = [],
    ssh_inbound_failed = [],
    ssh_outbound_history = [],
    ssh_outbound_active = [],
    installed_packages = []
  } = security;

  const Card = ({ children, redBorder }) => (
    <div style={{
      background: "var(--surface)",
      border: `1px solid ${redBorder ? "var(--red)" : "var(--border)"}`,
      borderRadius: "12px", padding: "16px"
    }}>
      {children}
    </div>
  );

  const Title = ({ icon, text, count, color = "var(--muted)" }) => (
    <div style={{ display: "flex", justifyContent: "space-between",
      alignItems: "center", marginBottom: "12px" }}>
      <div style={{ fontWeight: 600, fontSize: "14px" }}>{icon} {text}</div>
      <span style={{ fontSize: "11px", color,
        background: "var(--border)", padding: "2px 8px", borderRadius: "10px" }}>
        {count}
      </span>
    </div>
  );

  const Th = ({ cols }) => (
    <thead>
      <tr style={{ color: "var(--muted)" }}>
        {cols.map(h => (
          <th key={h} style={{ padding: "4px 6px", textAlign: "left",
            borderBottom: "1px solid var(--border)", fontWeight: 500,
            fontSize: "11px" }}>{h}</th>
        ))}
      </tr>
    </thead>
  );

  return (
    <div style={{ marginTop: "16px" }}>
      <div style={{ fontWeight: 700, fontSize: "16px",
        marginBottom: "12px" }}>🔐 Security Monitor</div>

      {/* Row 1 — Active Sessions + Sudo */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr",
        gap: "16px", marginBottom: "16px" }}>

        <Card>
          <Title icon="👤" text="Active Sessions"
            count={logged_in_users.length} color="var(--green)" />
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <Th cols={["User", "Terminal", "Login Time", "From"]} />
            <tbody>
              {logged_in_users.map((u, i) => (
                <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "5px 6px", color: "var(--green)",
                    fontWeight: 600, fontSize: "11px" }}>{u.user}</td>
                  <td className="mono" style={{ padding: "5px 6px",
                    color: "var(--muted)", fontSize: "11px" }}>{u.terminal}</td>
                  <td className="mono" style={{ padding: "5px 6px",
                    fontSize: "10px" }}>{u.login_time}</td>
                  <td style={{ padding: "5px 6px", color: "var(--blue)",
                    fontSize: "11px" }}>{u.from}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card>
          <Title icon="⚡" text="Sudo Commands"
            count={sudo_usage.length} color="var(--yellow)" />
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <Th cols={["Time", "User", "Command"]} />
              <tbody>
                {sudo_usage.map((s, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td className="mono" style={{ padding: "5px 6px",
                      color: "var(--muted)", fontSize: "10px",
                      whiteSpace: "nowrap" }}>
                      {s.timestamp.split(" ")[1]}
                    </td>
                    <td style={{ padding: "5px 6px",
                      color: "var(--yellow)", fontSize: "11px" }}>{s.user}</td>
                    <td className="mono" style={{ padding: "5px 6px",
                      fontSize: "10px", maxWidth: "200px",
                      overflow: "hidden", textOverflow: "ellipsis",
                      whiteSpace: "nowrap" }}>{s.command}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Row 2 — SSH Inbound */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr",
        gap: "16px", marginBottom: "16px" }}>

        <Card>
          <Title icon="✅" text="SSH Inbound — Success"
            count={ssh_inbound_success.length} color="var(--green)" />
          <div style={{ maxHeight: "180px", overflowY: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <Th cols={["Time", "User", "From IP", "Method"]} />
              <tbody>
                {ssh_inbound_success.length === 0 ? (
                  <tr><td colSpan={4} style={{ padding: "12px 6px",
                    color: "var(--muted)", textAlign: "center",
                    fontSize: "11px" }}>No successful SSH logins</td></tr>
                ) : ssh_inbound_success.map((s, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td className="mono" style={{ padding: "5px 6px",
                      color: "var(--muted)", fontSize: "10px" }}>
                      {s.timestamp.split(" ")[1]}
                    </td>
                    <td style={{ padding: "5px 6px",
                      color: "var(--green)", fontSize: "11px" }}>{s.user}</td>
                    <td className="mono" style={{ padding: "5px 6px",
                      color: "var(--blue)", fontSize: "11px" }}>{s.from_ip}</td>
                    <td style={{ padding: "5px 6px" }}>
                      <span style={{ fontSize: "9px", padding: "2px 5px",
                        borderRadius: "8px", border: "1px solid var(--green)",
                        color: "var(--green)" }}>{s.method}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        <Card redBorder={ssh_inbound_failed.length > 0}>
          <Title icon="❌" text="SSH Inbound — Failed"
            count={ssh_inbound_failed.length}
            color={ssh_inbound_failed.length > 0 ? "var(--red)" : "var(--muted)"} />
          <div style={{ maxHeight: "180px", overflowY: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <Th cols={["Time", "User", "From IP", "Reason"]} />
              <tbody>
                {ssh_inbound_failed.length === 0 ? (
                  <tr><td colSpan={4} style={{ padding: "12px 6px",
                    color: "var(--muted)", textAlign: "center",
                    fontSize: "11px" }}>No failed SSH attempts ✅</td></tr>
                ) : ssh_inbound_failed.map((s, i) => (
                  <tr key={i} style={{ borderBottom: "1px solid var(--border)",
                    background: "rgba(239,68,68,0.05)" }}>
                    <td className="mono" style={{ padding: "5px 6px",
                      color: "var(--muted)", fontSize: "10px" }}>
                      {s.timestamp.split(" ")[1]}
                    </td>
                    <td style={{ padding: "5px 6px",
                      color: "var(--red)", fontSize: "11px" }}>{s.user}</td>
                    <td className="mono" style={{ padding: "5px 6px",
                      color: "var(--yellow)", fontSize: "11px" }}>{s.from_ip}</td>
                    <td style={{ padding: "5px 6px" }}>
                      <span style={{ fontSize: "9px", padding: "2px 5px",
                        borderRadius: "8px", border: "1px solid var(--red)",
                        color: "var(--red)" }}>{s.reason}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* Row 3 — Outbound SSH + Packages */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr",
        gap: "16px" }}>

        <Card>
          <Title icon="🚀" text="SSH Outbound — History"
            count={ssh_outbound_history.length} color="var(--purple)" />
          {ssh_outbound_active.length > 0 && (
            <div style={{ marginBottom: "8px", padding: "6px 8px",
              background: "rgba(16,185,129,0.1)", borderRadius: "6px",
              fontSize: "11px", color: "var(--green)" }}>
              🟢 {ssh_outbound_active.length} active connection(s) right now
            </div>
          )}
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {ssh_outbound_history.map((s, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between",
                alignItems: "center", padding: "6px 0",
                borderBottom: "1px solid var(--border)", fontSize: "11px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <span style={{ color: "var(--purple)" }}>→</span>
                  <span className="mono" style={{ color: "var(--blue)" }}>
                    {s.target}
                  </span>
                </div>
                <span className="mono" style={{ color: "var(--muted)",
                  fontSize: "10px", maxWidth: "200px", overflow: "hidden",
                  textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {s.command}
                </span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <Title icon="📦" text="Installed Packages (apt)"
            count={installed_packages.length} color="var(--blue)" />
          <div style={{ maxHeight: "200px", overflowY: "auto" }}>
            {installed_packages.slice().reverse().map((p, i) => (
              <div key={i} style={{ padding: "7px 0",
                borderBottom: "1px solid var(--border)" }}>
                <div style={{ display: "flex", justifyContent: "space-between",
                  marginBottom: "4px" }}>
                  <span className="mono" style={{ fontSize: "10px",
                    color: "var(--muted)" }}>
                    {p.date?.split("  ")[0]}
                  </span>
                  <span className="mono" style={{ fontSize: "10px",
                    color: "var(--yellow)" }}>
                    {p.command?.replace("apt install ", "")
                      .replace("apt-get install ", "").slice(0, 30)}
                  </span>
                </div>
                <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
                  {(p.packages || [])
                    .filter(pkg => !pkg.startsWith("("))
                    .map((pkg, j) => (
                      <span key={j} style={{ fontSize: "9px", padding: "1px 5px",
                        borderRadius: "8px", background: "var(--border)",
                        color: "var(--blue)" }}>{pkg}</span>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
