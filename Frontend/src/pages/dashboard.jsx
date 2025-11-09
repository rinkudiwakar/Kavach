import React from "react";
import { Lock, Shield, Users, AlertTriangle, Mic, Eye } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "../css/Dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();

  return (
    <div className="dashboard-container">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-left">
          <Shield className="navbar-icon" />
          <h2 className="navbar-title">KAVACH</h2>
        </div>
        <div className="navbar-right">
          <button className="login-btn" onClick={() => navigate("/login")}>
            Login
          </button>
          <button className="get-started-small" onClick={() => navigate("/login")}>
            Get Started
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="dashboard-header-dark">
        <div className="dashboard-title-section">
          <Shield className="dashboard-icon-glow" />
          <h1 className="dashboard-title-glow">KAVACH</h1>
          <p className="dashboard-subtitle-dark">
            Voice-Authenticated Smart Home Security
          </p>
          <p className="dashboard-description">
            Next-generation security system powered by advanced voice recognition
            technology. Protect your home with the most natural authentication
            method — your voice.
          </p>

          {/* Buttons */}
          <div className="dashboard-buttons">
            <button
              className="get-started-btn"
              onClick={() => navigate("/login")}
            >
              Get Started
            </button>
            <button className="see-demo-btn">
              <Eye size={18} /> See Demo
            </button>
          </div>
        </div>
      </header>

      {/* Features Section */}
      <main className="features-section-dark">
        <h2 className="features-heading">Why Choose KAVACH?</h2>
        <p className="features-subheading">
          Advanced features for complete home security
        </p>

        <div className="features-grid">
          <div className="feature-card-dark">
            <Mic className="feature-icon-glow" />
            <h3>Voice Recognition</h3>
            <p>
              Advanced AI-powered voice authentication ensures only authorized
              family members can access your home.
            </p>
          </div>

          <div className="feature-card-dark">
            <Users className="feature-icon-glow" />
            <h3>Family Management</h3>
            <p>
              Manage family members, approve access requests, and monitor
              activities in real time.
            </p>
          </div>

          <div className="feature-card-dark">
            <Lock className="feature-icon-glow" />
            <h3>Smart Lock Integration</h3>
            <p>
              Seamlessly integrates with your smart lock system for secure,
              hands-free access control.
            </p>
          </div>

          <div className="feature-card-dark">
            <Shield className="feature-icon-glow" />
            <h3>Multi-layer Security</h3>
            <p>
              Voice keyword protection with backup PIN ensures access even when
              recognition isn’t available.
            </p>
          </div>

          <div className="feature-card-dark">
            <Eye className="feature-icon-glow" />
            <h3>Admin Controls</h3>
            <p>
              Admin dashboard with security settings and detailed access reports.
            </p>
          </div>

          <div className="feature-card-dark">
            <AlertTriangle className="feature-icon-glow" />
            <h3>Real-time Monitoring</h3>
            <p>
              Get instant alerts and monitor all access attempts with detailed
              logs.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
