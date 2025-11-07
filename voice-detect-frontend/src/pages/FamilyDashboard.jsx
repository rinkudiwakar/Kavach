import React from "react";
import { Users, Lock, Mic, Activity, Copy, ArrowLeft } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useNavigate } from "react-router-dom";
import "./FamilyDashboard.css";

const FamilyDashboard = () => {
  const navigate = useNavigate();

  const data = [
    { day: "Mon", attempts: 12 },
    { day: "Tue", attempts: 15 },
    { day: "Wed", attempts: 18 },
    { day: "Thu", attempts: 14 },
    { day: "Fri", attempts: 20 },
    { day: "Sat", attempts: 16 },
    { day: "Sun", attempts: 10 },
  ];

  return (
    <div className="family-dashboard">
    <header className="family-header">
  <h1 className="family-title">Family Dashboard</h1>
  <button
    className="back-btn"
    onClick={() => navigate("/dashboard/member")}
  >
    <ArrowLeft size={15} /> Back
  </button>
</header>

<p className="family-subtitle">The Sharma Family</p>

    
      {/* Top Stats */}
      <section className="stats-section">
        <div className="stat-card">
          <Users className="stat-icon" />
          <p>Total Members</p>
          <h2>4</h2>
        </div>

        <div className="stat-card">
          <Lock className="stat-icon" />
          <p>Door Status</p>
          <h2>🔒 Locked</h2>
        </div>

        <div className="stat-card">
          <Mic className="stat-icon" />
          <p>Mic Status</p>
          <h2>🎤 Active</h2>
        </div>

        <div className="stat-card">
          <Activity className="stat-icon" />
          <p>This Week</p>
          <h2>105</h2>
        </div>
      </section>

      {/* Info Section */}
      <section className="info-section">
        <div className="info-card">
          <h3>Family Token</h3>
          <div className="token-box">
            <input type="text" value="abc123xyz789" readOnly />
            <button className="copy-btn">
              <Copy size={18} />
            </button>
          </div>
          <p className="token-note">Share this token with new family members</p>
        </div>

        <div className="info-card">
          <h3>Latest Command</h3>
          <div className="latest-command">
            <p className="intent">Intent Detected</p>
            <p className="command">"open_door" by Rinku</p>
            <span className="time">2 minutes ago</span>
          </div>
        </div>
      </section>

      {/* Weekly Chart */}
      <section className="chart-section">
        <h3>Weekly Access Attempts</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#0f2926" />
            <XAxis dataKey="day" stroke="#00ffc3" />
            <YAxis stroke="#00ffc3" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="attempts"
              stroke="#00ffc3"
              strokeWidth={2}
              dot={{ fill: "#00ffc3" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </div>
  );
};

export default FamilyDashboard;
