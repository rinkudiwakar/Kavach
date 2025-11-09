import React, { useState, useEffect } from "react";
import { Shield, Edit, Trash2, Download, PlusCircle } from "lucide-react";
import "../css/AdminDashboard.css";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

const MAX_FILE_MB = 12; // Max upload size (MB)

const AdminDashboard = () => {
  const navigate = useNavigate();

  // ✅ Family members fetched from backend
  const [familyMembers, setFamilyMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [newMember, setNewMember] = useState({
    name: "",
    keyword: "",
    audio1: null,
    audio2: null,
    audio3: null,
  });
  const [adding, setAdding] = useState(false);

  // ✅ Fetch family members
  useEffect(() => {
    const fetchMembers = async () => {
      setLoading(true);
      try {
        const token = Cookies.get("token");
        const res = await fetch("http://localhost:5000/api/family/members", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.error || `Failed to fetch (${res.status})`);
        }

        const data = await res.json();
        const membersArr = Array.isArray(data) ? data : data.members || [];

        const normalized = membersArr.map((m) => ({
          name: m.name || "Unknown",
          keyword: m.keyword || "open",
          status: m.status || "Active",
          unlocks: typeof m.unlocks === "number" ? m.unlocks : 0,
        }));

        setFamilyMembers(normalized);
      } catch (err) {
        console.error("Fetch members error:", err);
        setError(err.message || "Failed to load members");
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, []);

  // ✅ Helper — Check File Size
  const fileTooLarge = (file) => file && file.size / 1024 / 1024 > MAX_FILE_MB;

  // ✅ Add Member
  const handleAddMember = async () => {
    if (
      !newMember.name ||
      !newMember.keyword ||
      !newMember.audio1 ||
      !newMember.audio2 ||
      !newMember.audio3
    ) {
      alert("Please fill in name, keyword, and upload all 3 voice samples!");
      return;
    }

    if (
      fileTooLarge(newMember.audio1) ||
      fileTooLarge(newMember.audio2) ||
      fileTooLarge(newMember.audio3)
    ) {
      alert(`Each file must be ≤ ${MAX_FILE_MB} MB`);
      return;
    }

    try {
      setAdding(true);
      const token = Cookies.get("token");

      const form = new FormData();
      form.append("name", newMember.name);
      form.append("keyword", newMember.keyword || "open");
      form.append("audio1", newMember.audio1);
      form.append("audio2", newMember.audio2);
      form.append("audio3", newMember.audio3);

      const res = await fetch("http://localhost:5000/api/family/add-member", {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: form,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `Failed to add member (${res.status})`);
      }

      const created = await res.json();

      const newEntry = {
        name: created.name || newMember.name,
        keyword: created.keyword || newMember.keyword,
        status: created.status || "Active",
        unlocks: created.unlocks ?? 0,
      };

      setFamilyMembers((prev) => [...prev, newEntry]);

      // Reset modal
      setNewMember({
        name: "",
        keyword: "",
        audio1: null,
        audio2: null,
        audio3: null,
      });
      setShowModal(false);
    } catch (err) {
      console.error("Add member error:", err);
      alert(err.message || "Failed to add member");
    } finally {
      setAdding(false);
    }
  };

  // ✅ Increment Unlock Counter
  const increaseUnlock = (index) => {
    const updated = [...familyMembers];
    updated[index].unlocks += 1;
    setFamilyMembers(updated);
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
        <p className="dashboard-subtitle">Manage family voice access</p>

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

      {loading && <p style={{ padding: 16 }}>Loading members...</p>}
      {error && <p style={{ color: "red", padding: 16 }}>{error}</p>}

      {/* Members Table */}
      <section className="section small-section">
        <div className="section-header compact-header">
          <h2>
            <Shield size={18} /> Family Members
          </h2>
          <button className="export-btn">
            <Download size={14} /> Export Report
          </button>
        </div>

        <table className="members-table compact-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Keyword</th>
              <th>Status</th>
              <th>Total Unlocks</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            {familyMembers.map((member, index) => (
              <tr key={index}>
                <td>{member.name}</td>
                <td>{member.keyword}</td>
                <td>
                  <span className={`status ${member.status.toLowerCase()}`}>
                    {member.status}
                  </span>
                </td>
                <td>{member.unlocks}</td>
                <td style={{ display: "flex", gap: "8px" }}>
                  <button className="edit">
                    <Edit size={12} /> Edit
                  </button>
                  <button className="remove">
                    <Trash2 size={12} /> Remove
                  </button>
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

      {/* Add Member Modal */}
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
              placeholder="Keyword (e.g. open)"
              value={newMember.keyword}
              onChange={(e) =>
                setNewMember({ ...newMember, keyword: e.target.value })
              }
            />

            <label>Upload Voice Sample 1 (.wav/.mp4):</label>
            <input
              type="file"
              accept="audio/*,video/mp4"
              onChange={(e) =>
                setNewMember({ ...newMember, audio1: e.target.files[0] })
              }
            />

            <label>Upload Voice Sample 2 (.wav/.mp4):</label>
            <input
              type="file"
              accept="audio/*,video/mp4"
              onChange={(e) =>
                setNewMember({ ...newMember, audio2: e.target.files[0] })
              }
            />

            <label>Upload Voice Sample 3 (.wav/.mp4):</label>
            <input
              type="file"
              accept="audio/*,video/mp4"
              onChange={(e) =>
                setNewMember({ ...newMember, audio3: e.target.files[0] })
              }
            />

            <div className="modal-actions">
              <button onClick={handleAddMember} disabled={adding}>
                {adding ? "Adding..." : "Add Member"}
              </button>
              <button
                className="cancel"
                onClick={() => {
                  setShowModal(false);
                  setNewMember({
                    name: "",
                    keyword: "",
                    audio1: null,
                    audio2: null,
                    audio3: null,
                  });
                }}
              >
                Cancel
              </button>
            </div>
            <p style={{ fontSize: 12, marginTop: 8 }}>
              Max file size: {MAX_FILE_MB} MB per file.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
