import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

// ✅ Import all pages
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import FamilyChoice from "./pages/FamilyChoice";
import CreateFamily from "./pages/CreateFamily";

import VoiceSetup from "./pages/VoiceSetup";
import MemberDashboard from "./pages/MemberDashboard";
import FamilyDashboard from "./pages/FamilyDashboard";
import TestVoiceAccess from "./pages/TestVoiceAccess";
import AdminDashboard from "./pages/AdminDashboard";
import SystemDashboard from "./pages/SystemDashboard"; 

const App = () => {
  return (
 
      <Routes>

        {/* ✅ default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" />} />

        {/* 🔐 Authentication */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* 🏠 General Dashboards */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/member" element={<MemberDashboard />} />
        <Route path="/dashboard/admin" element={<AdminDashboard />} />

        {/* 👨‍👩‍👧 Family Management */}
        <Route path="/family-choice" element={<FamilyChoice />} />
        <Route path="/create-family" element={<CreateFamily />} />
       
        <Route path="/family-dashboard" element={<FamilyDashboard />} />

        {/* 🎤 Voice Setup and Testing */}
        <Route path="/voice-setup" element={<VoiceSetup />} />
        <Route path="/test-voice-access" element={<TestVoiceAccess />} />

        {/* ⚙️ Admin System Overview */}
        <Route path="/system-dashboard" element={<SystemDashboard />} />
      </Routes>
   
  );
};

export default App;
