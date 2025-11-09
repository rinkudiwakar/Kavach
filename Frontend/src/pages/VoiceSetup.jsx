import React, { useRef, useState } from "react";
import "./VoiceSetup.css";
import { addMember, uploadVoiceSample } from "../../apis/api.js";
import { useNavigate } from "react-router-dom";

const VoiceSetup = () => {
  const [memberId, setMemberId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRef = useRef(null);
  const chunksRef = useRef([]);
  const navigate = useNavigate();

  const createMember = async () => {
    try {
      const res = await addMember({ name: "Test Member", keyword: "" });
      if (res.member_id) {
        setMemberId(res.member_id);
        alert("Member created: " + res.member_id);
      } else {
        alert("Create member failed");
      }
    } catch {
      alert("Create member error");
    }
  };

  const start = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mr = new MediaRecorder(stream);
    mediaRef.current = mr;
    chunksRef.current = [];
    mr.ondataavailable = (e) => chunksRef.current.push(e.data);
    mr.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: chunksRef.current[0]?.type || "audio/webm" });
      const file = new File([blob], "sample.webm", { type: blob.type });
      if (!memberId) {
        alert("Create a member first");
        return;
      }
      try {
        await uploadVoiceSample(memberId, file);
        alert("Upload done");
      } catch (err) {
        alert("Upload failed");
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

  return (
    <div className="voice-container">
      <h1>Quick Voice Setup</h1>
      <button onClick={createMember}>Create Member</button>
      <div>Member ID: {memberId}</div>
      <button onMouseDown={start} onMouseUp={stop}>
        {isRecording ? "Recording..." : "Hold to Record"}
      </button>
      <button onClick={() => navigate("/dashboard/member")}>Done</button>
    </div>
  );
};

export default VoiceSetup;
