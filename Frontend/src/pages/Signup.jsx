import React from "react";
import { useNavigate } from "react-router-dom";
import "../css/Auth.css";

const Signup = () => {
  const navigate = useNavigate();

  const handleSignup = (e) => {
    e.preventDefault(); // Prevents page reload
    // Add signup logic here (API call, validation, etc.)
    navigate("/family-choice"); // Redirect after signup
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-icon">🛡️</div>
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join KAVACH Smart Home Security</p>

        {/* Attach handleSignup to form */}
        <form className="auth-form" onSubmit={handleSignup}>
          <label>Full Name</label>
          <input type="text" placeholder="Enter your name" required />

          <label>Email</label>
          <input type="email" placeholder="Enter your email" required />

          <label>Password</label>
          <input type="password" placeholder="Create password" required />

          {/* Submit triggers handleSignup */}
          <button type="submit" className="auth-btn">
            Sign Up
          </button>
        </form>

        <p className="auth-switch">
          Already have an account?{" "}
          <span onClick={() => navigate("/")}>Sign in</span>
        </p>
      </div>
    </div>
  );
};

export default Signup;
