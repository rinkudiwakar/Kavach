import React from "react";
import { Lock, Shield, Users, Mic, Activity, Server } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./MemberDashboard.css";

const MemberDashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="member-dashboard">
      {/* Welcome Section */}
      <section className="welcome-section">
        <h1>Member Dashboard</h1>
        <p>Welcome back, Rinku 👋</p>
      </section>

      {/* Status Section */}
      <section className="status-section">
        <div className="status-card">
          <Lock size={32} color="#00ffc3" />
          <div>
            <p>Door Status</p>
            <h3>Locked</h3>
          </div>
        </div>

        <div className="status-card">
          <Mic size={32} color="#00ffc3" />
          <div>
            <p>Voice Status</p>
            <h3>Verified</h3>
          </div>
        </div>

        <div className="status-card">
          <Activity size={32} color="#00ffc3" />
          <div>
            <p>Total Unlocks</p>
            <h3>247</h3>
          </div>
        </div>
      </section>

      {/* Quick Actions & Recent Activity */}
      <section className="bottom-section">
        <div className="quick-actions">
          <h2>Quick Actions</h2>

          {/* ✅ Navigate to Test Voice Access */}
          <button
            className="action-btn"
            onClick={() => navigate("/test-voice-access")}
          >
            <Mic size={20} /> Test Voice Access
          </button>

          {/* ✅ Navigate to Family Dashboard */}
          <button
            className="secondary-btn"
            onClick={() => navigate("/family-dashboard")}
          >
            <Users size={20} /> View Family Dashboard
          </button>

          {/* ✅ Navigate to System Dashboard */}
          <button
            className="secondary-btn"
            onClick={() => navigate("/system-dashboard")}
          >
            <Server size={20} /> View System Dashboard
          </button>

          <button className="secondary-btn">
            <Shield size={20} /> Settings
          </button>
        </div>

        <div className="recent-activity">
          <h2>Recent Activity</h2>

          <div className="activity-item">
            <div className="left">
              <Activity size={20} color="#00ffc3" />
              <span className="status">Door unlocked</span>
            </div>
            <span className="time">2 hours ago</span>
          </div>

          <div className="activity-item">
            <div className="left">
              <Mic size={20} color="#00ffc3" />
              <span className="status">Voice verified</span>
            </div>
            <span className="time">Yesterday</span>
          </div>

          <div className="activity-item">
            <div className="left">
              <Activity size={20} color="#ff4d4d" />
              <span className="status failed">Failed attempt</span>
            </div>
            <span className="time">2 days ago</span>
          </div>
        </div>
      </section>
    </div>
  );
};

export default MemberDashboard;
