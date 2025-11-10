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
        Create a new family 
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
      </div>
    </div>
  );
};

export default FamilyChoice;
