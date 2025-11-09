import React from "react";
import { useNavigate } from "react-router-dom";
import "../css/Auth.css";
import {login, saveToken} from "../../apis/api";
import Cookies from "js-cookie";

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");


const handleSubmit = async (e) => {
  e.preventDefault();

  try {
    const res = await fetch("http://localhost:5000/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json();

    if (res.ok && data.token) {
      // Store JWT in cookies (expires in 7 days)
      Cookies.set("token", data.token, {
        expires: 7, // days
        secure: window.location.protocol === "https:", // only send over HTTPS
        sameSite: "strict", // prevent CSRF
      });

      // Redirect to dashboard
      navigate("/dashboard/admin");
    } else {
      alert(data.error || "Login failed");
    }
  } catch (err) {
    console.error(err);
    alert("Login failed. Please check your connection or credentials.");
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
