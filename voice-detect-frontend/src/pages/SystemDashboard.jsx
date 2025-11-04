import React from "react";
import {
  Server,
  Database,
  Cpu,
  AlertTriangle,
  Activity,
} from "lucide-react";
import "./SystemDashboard.css";

const SystemDashboard = () => {
  return (
    <div className="system-dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="dashboard-title">
          <Server size={36} className="dashboard-icon" />
          <h1>System Dashboard</h1>
        </div>
        <p className="dashboard-subtitle">
          Engineering & System Overview
        </p>
      </header>

      {/* Top Stats */}
      <div className="stats-container">
        <div className="stat-box">
          <Database className="stat-icon" />
          <p>Total Families</p>
          <h2>12</h2>
        </div>
        <div className="stat-box">
          <Activity className="stat-icon" />
          <p>Active Devices</p>
          <h2>8</h2>
        </div>
        <div className="stat-box">
          <Cpu className="stat-icon" />
          <p>CPU Usage</p>
          <h2>45%</h2>
        </div>
        <div className="stat-box alert">
          <AlertTriangle className="stat-icon" />
          <p>Alerts</p>
          <h2>2</h2>
        </div>
      </div>

      {/* System Resources + Voice Model */}
      <div className="main-grid">
        <div className="resources-section">
          <h3>
            <Cpu className="section-icon" /> System Resources
          </h3>

          <div className="resource">
            <p>CPU Usage</p>
            <div className="progress-bar">
              <div className="fill" style={{ width: "45%" }}></div>
            </div>
          </div>

          <div className="resource">
            <p>Memory</p>
            <div className="progress-bar">
              <div className="fill" style={{ width: "68%" }}></div>
            </div>
          </div>

          <div className="resource">
            <p>Storage</p>
            <div className="progress-bar">
              <div className="fill" style={{ width: "32%" }}></div>
            </div>
          </div>

          <div className="resource">
            <p>Network</p>
            <div className="progress-bar">
              <div className="fill" style={{ width: "89%" }}></div>
            </div>
          </div>
        </div>

        <div className="voice-model-section">
          <h3>Voice Model Status</h3>

          <div className="voice-item active">
            <p>Model Version</p>
            <span>v2.5.1</span>
            <span className="status">Active</span>
          </div>

          <div className="voice-item">
            <p>Dataset Size</p>
            <span>2,450 samples</span>
          </div>

          <div className="voice-item">
            <p>Last Training</p>
            <span>3 days ago</span>
          </div>

          <button className="retrain-btn">Trigger Model Retraining</button>
        </div>
      </div>

      {/* Alerts Section */}
      <div className="alerts-section">
        <h3>
          <AlertTriangle className="section-icon alert-icon" /> System Alerts
        </h3>

        <div className="alert-item">
          <AlertTriangle className="alert-symbol" />
          <div>
            <p className="alert-title">Low Storage Space</p>
            <p>
              Storage is at 85% capacity. Consider cleaning up old logs.
            </p>
            <small>2 hours ago</small>
          </div>
        </div>

        <div className="alert-item">
          <AlertTriangle className="alert-symbol" />
          <div>
            <p className="alert-title">Failed Upload Detected</p>
            <p>Voice sample upload failed for user ID: 4523</p>
            <small>5 hours ago</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemDashboard;
