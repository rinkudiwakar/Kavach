import React, { useState } from "react";
import { useNavigate } from "react-router-dom";



import Cookies from "js-cookie";
import "./Auth.css";


const Signup = () => {
  const navigate = useNavigate();

  // Controlled form state
  const [formData, setFormData] = useState({
    family_name: "",
    admin_name: "",
    email: "",
    password: "",
  });

  // Handle input change
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  // Handle form submit
  const handleSignup = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          family_name: formData.family_name,
          admin_name: formData.admin_name,
          email: formData.email,
          password: formData.password,
        }),
      });

      const data = await res.json();

      if (res.ok) {

        alert("Signup successful!");
        navigate("/dashboard/admin");}
       else {
        alert(data.error || "Signup failed.");
      }
    } catch (err) {
      console.error("Signup Error:", err);
      alert("Something went wrong during signup.");
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-icon">🛡️</div>
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">Join KAVACH Smart Home Security</p>

        <form className="auth-form" onSubmit={handleSignup}>
          <label>Family Name</label>
          <input
            type="text"
            name="family_name"
            placeholder="Enter family name"
            required
            value={formData.family_name}
            onChange={handleChange}
          />

          <label>Admin Name</label>
          <input
            type="text"
            name="admin_name"
            placeholder="Enter your name"
            required
            value={formData.admin_name}
            onChange={handleChange}
          />

          <label>Email</label>
          <input
            type="email"
            name="email"
            placeholder="Enter your email"
            required
            value={formData.email}
            onChange={handleChange}
          />

          <label>Password</label>
          <input
            type="password"
            name="password"
            placeholder="Create password"
            required
            value={formData.password}
            onChange={handleChange}
          />

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
