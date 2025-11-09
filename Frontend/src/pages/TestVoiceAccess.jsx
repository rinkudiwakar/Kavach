import React, { useState } from "react";
import { Mic } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./TestVoiceAccess.css";

const TestVoiceAccess = () => {
  const [isRecording, setIsRecording] = useState(false);
  const navigate = useNavigate();

  const handleMicClick = () => {
    setIsRecording(true);
    setTimeout(() => setIsRecording(false), 2000);
  };

  const handleBack = () => {
    navigate("/dashboard/member");
  };

  return (
    <div className="voice-test-container">
      <h1>Test Voice Access</h1>
      <p>Verify your voice authentication</p>

      {/* Voice Test Card */}
      <div className="voice-card">
        <div
          className={`mic-circle ${isRecording ? "recording" : ""}`}
          onClick={handleMicClick}
        >
          <Mic size={40} />
        </div>
        <h2>{isRecording ? "Listening..." : "Ready to Test"}</h2>
        <p>Click the microphone to start voice verification</p>
      </div>

      {/* Info Section */}
      <div className="info-section">
        <div className="tips">
          <h3>Tips for Better Recognition</h3>
          <ul>
            <li>Speak in a quiet environment</li>
            <li>Use your natural voice tone</li>
            <li>Maintain consistent distance from mic</li>
            <li>Speak clearly and at normal speed</li>
          </ul>
        </div>

        <div className="stats">
          <h3>Your Voice Stats</h3>
          <ul>
            <li>Samples Recorded: 20/20</li>
            <li>Verification Rate: 95%</li>
            <li>Last Updated: 2 days ago</li>
            <li>Status: Active</li>
          </ul>
        </div>
      </div>

      {/* Back Button */}
      <button className="back-btn" onClick={handleBack}>
        ⬅ Back to Member Dashboard
      </button>
    </div>
  );
};

export default TestVoiceAccess;
