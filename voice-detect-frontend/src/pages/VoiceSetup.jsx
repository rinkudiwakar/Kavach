import React, { useState } from "react";
import { Mic } from "lucide-react";
import { useNavigate } from "react-router-dom"; // ✅ import navigation
import "./VoiceSetup.css";

const sentences = [
  "The quick brown fox jumps over the lazy dog.",
  "Security begins with your voice.",
  "Kavach protects your family anytime, anywhere.",
  "Say hello to smart home protection.",
  "Your voice is your unique key.",
  "Technology meets trust with Kavach.",
  "Speak to unlock a safer world.",
  "Guardians listen when you speak.",
  "Authentication made easy and secure.",
  "Protecting your home with your command.",
];

const VoiceSetup = () => {
  const totalSamples = 10;
  const [currentSample, setCurrentSample] = useState(1);
  const [recordedSamples, setRecordedSamples] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const navigate = useNavigate(); // ✅ hook for navigation

  const handleRecord = () => {
    setIsRecording(true);
    setTimeout(() => {
      setIsRecording(false);
      setRecordedSamples((prev) =>
        prev.includes(currentSample) ? prev : [...prev, currentSample]
      );
    }, 1500); // Simulate recording
  };

  const handleNext = () => {
    if (currentSample < totalSamples) setCurrentSample((prev) => prev + 1);
  };

  const handlePrev = () => {
    if (currentSample > 1) setCurrentSample((prev) => prev - 1);
  };

  const handleUpload = () => {
    if (recordedSamples.length < totalSamples) {
      alert("Please record all samples before uploading.");
      return;
    }
    alert("All samples uploaded successfully!");
    navigate("/dashboard/member"); // ✅ navigate to member dashboard
  };

  const progress = (recordedSamples.length / totalSamples) * 100;

  return (
    <div className="voice-container">
      {/* Header */}
      <div className="voice-header">
        <h1>Voice Sample Recording</h1>
        <p>Record {totalSamples} voice samples for accurate authentication</p>
      </div>

      {/* Progress Bar */}
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>

      {/* Recording Section */}
      <div className="record-box">
        <p className="sample-text">
          Sample {currentSample} of {totalSamples}
        </p>

        <div className="sentence-box">“{sentences[currentSample - 1]}”</div>

        <button
          className={`record-btn ${isRecording ? "recording" : ""}`}
          onClick={handleRecord}
        >
          <Mic size={32} />
        </button>

        <div className="nav-btns">
          <button onClick={handlePrev} disabled={currentSample === 1}>
            Previous
          </button>
          <button onClick={handleNext} disabled={currentSample === totalSamples}>
            Next
          </button>
        </div>
      </div>

      {/* Sample Dots */}
      <div className="sample-status">
        {Array.from({ length: totalSamples }, (_, i) => (
          <div
            key={i}
            className={`sample-dot ${
              recordedSamples.includes(i + 1)
                ? "active"
                : currentSample === i + 1
                ? "current"
                : ""
            }`}
          ></div>
        ))}
      </div>

      {/* Upload Button */}
      <button className="upload-btn" onClick={handleUpload}>
        Upload All Samples ({recordedSamples.length}/{totalSamples})
      </button>
    </div>
  );
};

export default VoiceSetup;
