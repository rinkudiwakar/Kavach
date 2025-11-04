import React from "react";
import { Users, KeyRound, Shield, Eye, Edit, Trash2, Download } from "lucide-react";
import "./AdminDashboard.css";

const AdminDashboard = () => {
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
      {/* Pending Join Requests */}
      <section className="section">
        <div className="section-header">
          <h2><Users size={20} /> Pending Join Requests</h2>
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
      <section className="section">
        <div className="section-header">
          <h2><Shield size={20} /> Family Members</h2>
          <button className="export-btn">
            <Download size={16} /> Export Report
          </button>
        </div>

        <table className="members-table">
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
                  <button className="edit"><Edit size={14} /> Edit</button>
                  <button className="remove"><Trash2 size={14} /> Remove</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* Security Settings */}
      <section className="section grid-2">
        <div className="security-card">
          <h3><KeyRound size={18} /> Security Settings</h3>
          <button className="security-btn">Change Voice Keyword</button>
          <button className="security-btn">Update Backup Password</button>
          <button className="security-btn">Security Audit Log</button>
        </div>

        <div className="security-card">
          <h3><Eye size={18} /> Keyword Visibility Requests</h3>
          <div className="request-box">
            <p><strong>Neha Sharma</strong> requested to view the family keyword</p>
            <div className="action-buttons">
              <button className="approve">Approve</button>
              <button className="reject">Deny</button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AdminDashboard;
