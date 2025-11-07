import React, { useState } from "react";
import {
  Shield,
  Edit,
  Trash2,
  Download,
  PlusCircle,
} from "lucide-react";
import "../css/AdminDashboard.css";
import { useNavigate } from "react-router-dom";

const AdminDashboard = () => {
  const navigate = useNavigate();

  // ✅ Default: Admin only
  const [familyMembers, setFamilyMembers] = useState([
    { name: "Rinku (You)", role: "Admin", status: "Active", unlocks: 247 },
  ]);

  // Modal
  const [showModal, setShowModal] = useState(false);
  const [newMember, setNewMember] = useState({
    name: "",
    voice1: null,
    voice2: null,
    voice3: null,
  });

  const handleAddMember = () => {
    if (
      !newMember.name ||
      !newMember.voice1 ||
      !newMember.voice2 ||
      !newMember.voice3
    ) {
      alert("Please enter name and upload all 3 voice samples!");
      return;
    }

    setFamilyMembers([
      ...familyMembers,
      {
        name: newMember.name,
        role: "Member",
        status: "Active",
        unlocks: 0,
      },
    ]);

    setNewMember({ name: "", voice1: null, voice2: null, voice3: null });
    setShowModal(false);
  };

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

      {/* Header */}
      <header className="dashboard-header">
        <h1 className="dashboard-title">Admin Dashboard</h1>
        <p className="dashboard-subtitle">Manage registered members</p>

        <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
          <button
            className="member-dashboard-btn"
            onClick={() => navigate("/dashboard/member")}
          >
            Go to Member Dashboard
          </button>

          <button className="add-member-btn" onClick={() => setShowModal(true)}>
            <PlusCircle size={16} /> Add Member
          </button>
        </div>
      </header>

      {/* ✅ Family Members Table */}
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

      {/* ✅ Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add New Member</h3>

            <input
              type="text"
              placeholder="Member Name"
              value={newMember.name}
              onChange={(e) =>
                setNewMember({ ...newMember, name: e.target.value })
              }
            />

            <label>Upload Voice Sample 1:</label>
            <input
              type="file"
              accept="audio/*"
              onChange={(e) =>
                setNewMember({ ...newMember, voice1: e.target.files[0] })
              }
            />

            <label>Upload Voice Sample 2:</label>
            <input
              type="file"
              accept="audio/*"
              onChange={(e) =>
                setNewMember({ ...newMember, voice2: e.target.files[0] })
              }
            />

            <label>Upload Voice Sample 3:</label>
            <input
              type="file"
              accept="audio/*"
              onChange={(e) =>
                setNewMember({ ...newMember, voice3: e.target.files[0] })
              }
            />

            <div className="modal-actions">
              <button onClick={handleAddMember}>Add Member</button>
              <button className="cancel" onClick={() => setShowModal(false)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default AdminDashboard;
