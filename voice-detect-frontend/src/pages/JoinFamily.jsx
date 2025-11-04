import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Key } from "lucide-react";
import "./JoinFamily.css";

const JoinFamily = () => {
  const [familyToken, setFamilyToken] = useState("");
  const navigate = useNavigate();

  const handleJoin = (e) => {
    e.preventDefault();

    if (!familyToken.trim()) {
      alert("Please enter a valid family token or invite URL.");
      return;
    }

    // Later you can replace this with backend validation logic
    console.log("Joining family with token:", familyToken);

    // After successful join, navigate to dashboard
    navigate("/dashboard");
  };

  return (
    <div className="join-family-container">
      <div className="join-family-card">
        <div className="join-family-header">
          <Key className="join-icon" />
          <h1>Join a Family</h1>
          <p>Enter the family token to request access</p>
        </div>

        <form onSubmit={handleJoin} className="join-form">
          <label>Family Token</label>
          <input
            type="text"
            placeholder="Enter family token or invite URL"
            value={familyToken}
            onChange={(e) => setFamilyToken(e.target.value)}
          />
          <p className="token-hint">Get this token from your family admin</p>

          <div className="info-box">
            <h3>What happens next?</h3>
            <ul>
              <li>Your request will be sent to the family admin</li>
              <li>Admin will review and approve/reject</li>
              <li>Once approved, you'll record voice samples</li>
              <li>After setup, you'll get secure access</li>
            </ul>
          </div>

          <button type="submit" className="join-btn">
            Send Join Request
          </button>
        </form>
      </div>
    </div>
  );
};

export default JoinFamily;
