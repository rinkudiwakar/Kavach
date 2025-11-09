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

  // ✅ Family Members (default admin)
  const [familyMembers, setFamilyMembers] = useState([
    { name: "Rinku (You)", relationship: "You", status: "Active", unlocks: 2},
  ]);

  // Modal
  const [showModal, setShowModal] = useState(false);
  const [newMember, setNewMember] = useState({
    name: "",
    relationship: "",
    voice1: null,
    voice2: null,
    voice3: null,
  });

  // ✅ Add New Member
  const handleAddMember = () => {
    if (
      !newMember.name ||
      !newMember.relationship ||
      !newMember.voice1 ||
      !newMember.voice2 ||
      !newMember.voice3
    ) {
      alert("Please enter name, relationship, and upload all 3 voice samples!");
      return;
    }

    setFamilyMembers([
      ...familyMembers,
      {
        name: newMember.name,
        relationship: newMember.relationship,
        status: "Active",
        unlocks: 0,
      },
    ]);

    setNewMember({
      name: "",
      relationship: "",
      voice1: null,
      voice2: null,
      voice3: null,
    });
    setShowModal(false);
  };

  // ✅ Increase Unlock Count Dynamically
  const increaseUnlock = (index) => {
    const updated = [...familyMembers];
    updated[index].unlocks += 1;
    setFamilyMembers(updated);
  };

  return (
    <div className="admin-dashboard">

      {/* NAVBAR */}
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

      {/* HEADER */}
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

      {/* ✅ FAMILY MEMBERS TABLE */}
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
              <th>Relationship</th>
              <th>Status</th>
              <th>Total Unlocks</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {familyMembers.map((member, index) => (
              <tr key={index}>
                <td>{member.name}</td>
                <td>{member.relationship}</td>
                <td>
                  <span className={`status ${member.status.toLowerCase()}`}>
                    {member.status}
                  </span>
                </td>

                <td>{member.unlocks}</td>

                <td style={{ display: "flex", gap: "8px" }}>
                  <button className="edit"><Edit size={12} /> Edit</button>
                  <button className="remove"><Trash2 size={12} /> Remove</button>
                  <button
                    className="approve"
                    onClick={() => increaseUnlock(index)}
                  >
                    + Unlock
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {/* ✅ MODAL */}
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

            <input
              type="text"
              placeholder="Relationship (Father, Mother, etc.)"
              value={newMember.relationship}
              onChange={(e) =>
                setNewMember({ ...newMember, relationship: e.target.value })
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
