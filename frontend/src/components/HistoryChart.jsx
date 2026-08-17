import { LineChart, Line, XAxis, YAxis, Tooltip,
         ResponsiveContainer, Legend, CartesianGrid } from "recharts";
export default function HistoryChart({ history }) {
  const data = (history || []).map(h => ({
    time: h.time?.split(" ")[1] || h.time,
    CPU: parseFloat(h.cpu?.toFixed(1)),
    RAM: parseFloat(h.ram?.toFixed(1))
  }));
  return (
    <div style={{
      background: "var(--surface)", border: "1px solid var(--border)",
      borderRadius: "12px", padding: "20px"
    }}>
      <div style={{ fontWeight: 600, marginBottom: "16px", fontSize: "14px" }}>
        📈 Live History (last 5 min)
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: "var(--muted)" }}
            interval="preserveStartEnd" />
          <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "var(--muted)" }}
            tickFormatter={v => `${v}%`} />
          <Tooltip
            contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)",
              borderRadius: "8px", fontSize: "12px" }}
            formatter={(v) => [`${v}%`]}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          <Line type="monotone" dataKey="CPU" stroke="var(--blue)" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="RAM" stroke="var(--purple)" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
