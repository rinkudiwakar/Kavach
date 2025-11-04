import React from "react";
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import FamilyChoice from "./pages/FamilyChoice";
import CreateFamily from "./pages/CreateFamily";
import JoinFamily from "./pages/JoinFamily";

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/family-choice" element={<FamilyChoice />} />
      <Route path="/create-family" element={<CreateFamily />} />
      <Route path="/join-family" element={<JoinFamily />} />
    </Routes>
  );
};

export default App;
