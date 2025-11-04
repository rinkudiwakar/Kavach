import React from "react";
import { useNavigate } from "react-router-dom";
import { Users, UserPlus } from "lucide-react";
import "./FamilyChoice.css";

const FamilyChoice = () => {
  const navigate = useNavigate();

  return (
    <div className="family-choice-container">
      <h1 className="family-choice-title">Choose Your Path</h1>
      <p className="family-choice-subtitle">
        Create a new family or join an existing one
      </p>

      <div className="family-choice-grid">
        {/* Create a Family */}
        <div className="family-card create">
          <Users className="family-icon" />
          <h2>Create a Family</h2>
          <p>
            Set up your own family security system and become the admin
          </p>
          <ul>
            <li>✓ Generate unique family token</li>
            <li>✓ Set voice keyword</li>
            <li>✓ Record voice samples</li>
            <li>✓ Manage family members</li>
          </ul>
          <button
            className="family-btn create-btn"
            onClick={() => navigate("/create-family")}
          >
            Create Family
          </button>
        </div>

        {/* Join a Family */}
        <div className="family-card join">
          <UserPlus className="family-icon" />
          <h2>Join a Family</h2>
          <p>
            Enter a family token to join an existing security system
          </p>
          <ul>
            <li>✓ Enter family token or URL</li>
            <li>✓ Request admin approval</li>
            <li>✓ Record your voice samples</li>
            <li>✓ Get secure access</li>
          </ul>
          <button
            className="family-btn join-btn"
            onClick={() => navigate("/join-family")}
          >
            Join Family
          </button>
        </div>
      </div>
    </div>
  );
};

export default FamilyChoice;
