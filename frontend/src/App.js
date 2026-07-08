import { useState, useEffect, useRef } from "react";
import "./App.css";

const API_KEY = "sos-secret-key-2024";
const WS_URL = `ws://localhost:8080/ws?api_key=${API_KEY}`;
const API_URL = "http://localhost:8080";

const LABELS = {
  scream: { text: "צרחה", color: "#e74c3c" },
  crying: { text: "בכי", color: "#e67e22" },
  explosion: { text: "פיצוץ", color: "#c0392b" },
  background: { text: "רקע", color: "#27ae60" },
};

export default function App() {
  const [isListening, setIsListening] = useState(false);
  const [result, setResult] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket(WS_URL);
    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setResult(data);
      if (data.alert) {
        setAlerts((prev) => [
          { ...data, time: new Date().toLocaleTimeString() },
          ...prev.slice(0, 9),
        ]);
      }
    };
    return () => ws.current.close();
  }, []);

  const toggle = async () => {
    const endpoint = isListening ? "stop" : "start";
    await fetch(`${API_URL}/${endpoint}`, {
      method: "POST",
      headers: { "X-API-Key": API_KEY },
    });
    setIsListening(!isListening);
  };

  return (
    <div className="app">
      <h1>🚨 SOS Audio Detection</h1>

      <button className={`btn ${isListening ? "btn-stop" : "btn-start"}`} onClick={toggle}>
        {isListening ? "⏹ עצור האזנה" : "▶ התחל האזנה"}
      </button>

      {result && (
        <div className="result" style={{ borderColor: LABELS[result.label]?.color }}>
          <div className="label" style={{ color: LABELS[result.label]?.color }}>
            {result.alert ? "🚨 " : ""}{LABELS[result.label]?.text}
          </div>
          <div className="confidence">{result.confidence}% ביטחון</div>
          <div className="probs">
            {Object.entries(result.probs).map(([cat, prob]) => (
              <div key={cat} className="prob-row">
                <span>{LABELS[cat]?.text}</span>
                <div className="bar-bg">
                  <div className="bar" style={{ width: `${prob}%`, background: LABELS[cat]?.color }} />
                </div>
                <span>{prob}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {alerts.length > 0 && (
        <div className="alerts">
          <h2>היסטוריית התרעות</h2>
          {alerts.map((a, i) => (
            <div key={i} className="alert-item" style={{ borderColor: LABELS[a.label]?.color }}>
              <span>{a.time}</span>
              <span style={{ color: LABELS[a.label]?.color }}>{LABELS[a.label]?.text}</span>
              <span>{a.confidence}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
