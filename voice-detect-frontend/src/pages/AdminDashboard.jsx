import React from "react";
import {
  Users,
  Shield,
  Edit,
  Trash2,
  Download,
} from "lucide-react";
import "../css/AdminDashboard.css";
import { useNavigate } from "react-router-dom";

const AdminDashboard = () => {
  const navigate = useNavigate();

  const familyMembers = [
    { name: "Rinku (You)", role: "Admin", status: "Active", unlocks: 247 },
    { name: "Neha Sharma", role: "Member", status: "Active", unlocks: 180 },
    { name: "Raj Sharma", role: "Member", status: "Active", unlocks: 156 },
  ];

  const joinRequests = [
    { name: "Priya Sharma", email: "priya@example.com", date: "2024-01-15" },
    { name: "Amit Kumar", email: "amit@example.com", date: "2024-01-14" },
  ];

  return (
    <div className="admin-dashboard">
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

      {/* Dashboard Header */}
      <header className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Admin Dashboard</h1>
          <p className="dashboard-subtitle">Manage your family security system</p>
        </div>

        {/* ✅ Member Dashboard Button */}
        <button
          className="member-dashboard-btn"
          onClick={() => navigate("/dashboard/member")}
        >
          Go to Member Dashboard
        </button>
      </header>

      {/* Pending Join Requests */}
      <section className="section small-section">
        <div className="section-header compact-header">
          <h2><Users size={18} /> Pending Join Requests</h2>
          <span className="badge">{joinRequests.length}</span>
        </div>

        {joinRequests.map((req, index) => (
          <div className="request-card" key={index}>
            <div>
              <h4>{req.name}</h4>
              <p>{req.email}</p>
              <small>Requested on {req.date}</small>
            </div>
            <div className="action-buttons">
              <button className="approve">Approve</button>
              <button className="reject">Reject</button>
            </div>
          </div>
        ))}
      </section>

      {/* Family Members */}
      <section className="section small-section">
        <div className="section-header compact-header">
          <h2><Shield size={18} /> Family Members</h2>
          <button className="export-btn">
            <Download size={14} /> Export Report
          </button>
        </div>

        <table className="members-table compact-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Total Unlocks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {familyMembers.map((member, index) => (
              <tr key={index}>
                <td>{member.name}</td>
                <td>
                  <span className={`role ${member.role.toLowerCase()}`}>
                    {member.role}
                  </span>
                </td>
                <td>
                  <span className={`status ${member.status.toLowerCase()}`}>
                    {member.status}
                  </span>
                </td>
                <td>{member.unlocks}</td>
                <td>
                  <button className="edit"><Edit size={12} /> Edit</button>
                  <button className="remove"><Trash2 size={12} /> Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
};

export default AdminDashboard;
