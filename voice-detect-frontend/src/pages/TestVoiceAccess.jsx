import React, { useRef, useState } from "react";
import "./TestVoiceAccess.css";
import { verifyVoice } from "../lib/api";
import { useNavigate } from "react-router-dom";

const TestVoiceAccess = () => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const navigate = useNavigate();

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream);
    mediaRef.current = mr;
    chunksRef.current = [];
    mr.ondataavailable = (e) => chunksRef.current.push(e.data);
    mr.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: chunksRef.current[0]?.type || "audio/webm" });
      const file = new File([blob], "verify.webm", { type: blob.type });
      try {
        const res = await verifyVoice(file);
        alert(JSON.stringify(res));
      } catch (err) {
        alert("Verify failed");
        console.error(err);
      }
    };
    mr.start();
    setIsRecording(true);
  };

  const stop = () => {
    mediaRef.current?.stop();
    setIsRecording(false);
  };

  const handleBack = () => navigate("/dashboard/member");

  return (
    <div className="voice-test-container">
      <h1>Test Voice Access</h1>
      <p>Verify your voice authentication</p>

      <div className="voice-card">
        <div className={`mic-circle ${isRecording ? "recording" : ""}`} onMouseDown={start} onMouseUp={stop}>
          🎤
        </div>
        <h2>{isRecording ? "Listening..." : "Ready to Test"}</h2>
        <p>Hold the microphone button to record and verify</p>
      </div>

      <button className="back-btn" onClick={handleBack}>⬅ Back to Member Dashboard</button>
    </div>
  );
};

export default TestVoiceAccess;
