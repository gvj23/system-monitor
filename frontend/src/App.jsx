import { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import MetricCard from "./components/MetricCard";
import HistoryChart from "./components/HistoryChart";
import CPUCoreChart from "./components/CPUCoreChart";
import ProcessTable from "./components/ProcessTable";
import PortsTable from "./components/PortsTable";
import SecurityPanel from "./components/SecurityPanel";
import "./index.css";

const WS_URL = "ws://localhost:8000/ws";
const API_URL = "http://localhost:8000";

export default function App() {
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState([]);
  const [agentStatus, setAgentStatus] = useState("offline");
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  useEffect(() => {
    fetch(`${API_URL}/metrics`)
      .then(r => r.json())
      .then(d => {
        if (d.status === "ok") {
          setMetrics(d.data);
          setHistory(d.history || []);
          setAgentStatus(d.agent_status);
        }
      }).catch(console.error);
  }, []);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;
      ws.onopen = () => { setConnected(true); };
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === "metrics" || msg.type === "initial") {
          setMetrics(msg.data);
          setHistory(msg.history || []);
          setAgentStatus(msg.agent_status || "online");
        }
      };
      ws.onclose = () => { setConnected(false); setTimeout(connect, 3000); };
      ws.onerror = () => ws.close();
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  const cpu = metrics?.cpu;
  const ram = metrics?.ram;
  const disk = metrics?.disk;
  const net = metrics?.network_io;

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Header data={metrics} agentStatus={agentStatus} />
      <div style={{
        textAlign: "center", padding: "4px",
        background: connected ? "#052e16" : "#1f1115",
        fontSize: "11px",
        color: connected ? "var(--green)" : "var(--red)"
      }}>
        {connected ? "⚡ Live — WebSocket connected" : "⏳ Connecting to live feed..."}
      </div>

      <div style={{ padding: "20px", maxWidth: "1400px", margin: "0 auto" }}>
        {!metrics && (
          <div style={{ textAlign: "center", padding: "60px",
            color: "var(--muted)", fontSize: "14px" }}>
            ⏳ Waiting for agent to send data...
            <div style={{ marginTop: "8px", fontSize: "12px" }}>
              Make sure agent.py is running
            </div>
          </div>
        )}

        {metrics && (
          <>
            <div style={{ display: "flex", gap: "16px", flexWrap: "wrap", marginBottom: "16px" }}>
              <MetricCard title="CPU" icon="⚙️" percent={cpu?.usage_percent}
                color="var(--blue)" details={[
                  { label: "Cores", value: `${cpu?.physical_cores}P / ${cpu?.core_count}L` },
                  { label: "Frequency", value: `${cpu?.frequency_mhz} MHz` },
                ]} />
              <MetricCard title="RAM" icon="💾" percent={ram?.usage_percent}
                color="var(--purple)" details={[
                  { label: "Used", value: `${ram?.used_gb} GB` },
                  { label: "Total", value: `${ram?.total_gb} GB` },
                  { label: "Free", value: `${ram?.available_gb} GB` },
                ]} />
              <MetricCard title="Disk" icon="💿" percent={disk?.usage_percent}
                color="var(--green)" details={[
                  { label: "Used", value: `${disk?.used_gb} GB` },
                  { label: "Total", value: `${disk?.total_gb} GB` },
                  { label: "Free", value: `${disk?.free_gb} GB` },
                ]} />
              {net && (
                <div style={{
                  background: "var(--surface)", border: "1px solid var(--border)",
                  borderRadius: "12px", padding: "20px", flex: 1, minWidth: "220px"
                }}>
                  <div style={{ fontWeight: 600, marginBottom: "12px", fontSize: "14px" }}>
                    🌐 Network
                  </div>
                  {[
                    { label: "↑ Sent", value: `${net.bytes_sent_mb} MB` },
                    { label: "↓ Recv", value: `${net.bytes_recv_mb} MB` },
                    { label: "Pkts Sent", value: net.packets_sent?.toLocaleString() },
                    { label: "Pkts Recv", value: net.packets_recv?.toLocaleString() },
                  ].map((d, i) => (
                    <div key={i} style={{
                      display: "flex", justifyContent: "space-between",
                      fontSize: "12px", color: "var(--muted)", marginBottom: "6px"
                    }}>
                      <span>{d.label}</span>
                      <span className="mono" style={{ color: "var(--text)" }}>{d.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr",
              gap: "16px", marginBottom: "16px" }}>
              <HistoryChart history={history} />
              <CPUCoreChart cores={metrics?.cpu_cores} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <ProcessTable processes={metrics?.processes} />
              <PortsTable ports={metrics?.ports} />
            </div>

            {metrics?.system_errors?.length > 0 && (
              <div style={{
                marginTop: "16px", background: "var(--surface)",
                border: "1px solid var(--red)", borderRadius: "12px", padding: "16px"
              }}>
                <div style={{ fontWeight: 600, color: "var(--red)",
                  marginBottom: "8px", fontSize: "14px" }}>
                  ⚠️ System Errors Today
                </div>
                {metrics.system_errors.map((err, i) => (
                  <div key={i} className="mono" style={{
                    fontSize: "11px", color: "var(--muted)", padding: "4px 0",
                    borderBottom: i < metrics.system_errors.length - 1
                      ? "1px solid var(--border)" : "none"
                  }}>{err}</div>
                ))}
              </div>
            )}
          <SecurityPanel security={metrics?.security} />
          </>
        )}
      </div>
    </div>
  );
}
