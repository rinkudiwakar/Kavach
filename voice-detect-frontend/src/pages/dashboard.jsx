import React from "react";
import { Lock, Shield, Users, AlertTriangle } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div>
            <h1 className="title">Voice Lock Dashboard</h1>
            <p className="subtitle">
              Secure your home with biometric voice authentication
            </p>

            {/* Get Started Button */}
            <button
              className="get-started-btn"
              onClick={() => navigate("/")}
            >
              Get Started
            </button>
          </div>
          <div className="lock-status">
            <Lock className="lock-icon" />
            <span>Door Locked</span>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="main">
        <div className="stats-grid">
          <div className="stat-card">
            <Users className="stat-icon" />
            <h3>Family Members</h3>
            <p className="stat-number">0</p>
            <p className="stat-desc">Registered users</p>
          </div>

          <div className="stat-card">
            <Shield className="stat-icon green" />
            <h3>Security Status</h3>
            <p className="stat-number green">Active</p>
            <p className="stat-desc">All systems operational</p>
          </div>

          <div className="stat-card">
            <AlertTriangle className="stat-icon yellow" />
            <h3>Recent Alerts</h3>
            <p className="stat-number">0</p>
            <p className="stat-desc">In the last 24 hours</p>
          </div>
        </div>

        <div className="action-grid">
          <div className="action-card">
            <h4>Register Family Members</h4>
            <p>Add new members and configure their access</p>
            <button className="primary-btn">Add New Member</button>
          </div>

          <div className="action-card">
            <h4>Voice Enrollment</h4>
            <p>Record voice samples for authentication</p>
            <button className="secondary-btn">Start Enrollment</button>
          </div>

          <div className="action-card">
            <h4>Unlock Keyword</h4>
            <p>
              Current phrase: <strong>"Hi Di, open the door"</strong>
            </p>
            <button className="secondary-btn">Change Keyword</button>
          </div>

          <div className="action-card">
            <h4>Security Logs</h4>
            <p>View recent access attempts and activity</p>
            <button className="secondary-btn">View All Logs</button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
