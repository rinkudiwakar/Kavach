import React, { useState } from "react";
import { Shield, Key, Mic } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./CreateFamily.css";

const CreateFamily = () => {
  const [familyToken] = useState("z7zgmcif3a"); // example token
  const navigate = useNavigate();

  const handleContinue = (e) => {
    e.preventDefault();
    // TODO: Add API call to save family data
    navigate("/voice-setup"); // navigate to next step
  };

  return (
    <div className="create-family-container">
      <h1 className="create-title">Create Your Family</h1>
      <p className="create-subtitle">Set up your family security system</p>

      <form className="create-form" onSubmit={handleContinue}>
        {/* Family Info */}
        <div className="form-section">
          <div className="section-header">
            <Shield size={20} />
            <h2>Family Information</h2>
          </div>

          <label>Family Name *</label>
          <input type="text" placeholder="e.g., The Sharma Family" required />

          <label>Description</label>
          <textarea placeholder="Brief description of your family"></textarea>

          <label>Location (Optional)</label>
          <input type="text" placeholder="e.g., Mumbai, India" />
        </div>

        {/* Family Token */}
        <div className="form-section">
          <div className="section-header">
            <Key size={20} />
            <h2>Family Token</h2>
          </div>

          <div className="token-box">
            <input type="text" value={familyToken} readOnly />
            <button
              type="button"
              onClick={() => navigator.clipboard.writeText(familyToken)}
              className="copy-btn"
            >
              📋
            </button>
          </div>
          <p className="token-info">
            Share this token with family members to let them join
          </p>
        </div>

        {/* Voice Keyword */}
        <div className="form-section">
          <div className="section-header">
            <Mic size={20} />
            <h2>Voice Keyword</h2>
          </div>

          <label>Voice Command Keyword *</label>
          <input type="text" placeholder='e.g., "Open Kavach"' required />

          <label>Backup Password</label>
          <input type="password" placeholder="Emergency backup password" />
          <p className="token-info">
            Optional fallback when voice recognition fails
          </p>
        </div>

        <button type="submit" className="continue-btn">
          Continue to Voice Setup
        </button>
      </form>
    </div>
  );
};

export default CreateFamily;
