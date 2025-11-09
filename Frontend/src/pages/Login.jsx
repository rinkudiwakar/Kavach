import React from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css";
import {login, saveToken} from "../../apis/api";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await login({ email, password });
      if (res.token) {
        saveToken(res.token);
        navigate("/dashboard/admin"); // or adjust based on role
      } else {
        alert(res.error || "Login failed");
      }
    } catch (err) {
      alert(err.data?.error || "Login failed");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-icon">🔒</div>
        <h1 className="auth-title">Welcome to KAVACH</h1>
        <p className="auth-subtitle">Voice-Authenticated Smart Home Security</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>Email</label>
          <input value={email} onChange={(e)=>setEmail(e.target.value)} type="email" placeholder="Enter your email" required />

          <label>Password</label>
          <input value={password} onChange={(e)=>setPassword(e.target.value)} type="password" placeholder="Enter your password" required />

          <button type="submit" className="auth-btn">Sign In</button>
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
