import React from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css";

const Login = () => {
  const navigate = useNavigate();

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-icon">🔒</div>
        <h1 className="auth-title">Welcome to KAVACH</h1>
        <p className="auth-subtitle">Voice-Authenticated Smart Home Security</p>

        <form className="auth-form">
          <label>Email</label>
          <input type="email" placeholder="Enter your email" required />

          <label>Password</label>
          <input type="password" placeholder="Enter your password" required />

          {/* ✅ Navigate to Admin Dashboard after successful login */}
          <button
            type="button"
            className="auth-btn"
            onClick={() => navigate("/dashboard/admin")}
          >
            Sign In
          </button>
        </form>

        <p className="auth-switch">
          Don’t have an account?{" "}
          <span onClick={() => navigate("/signup")}>Sign up</span>
        </p>
      </div>
    </div>
  );
};

export default Login;
