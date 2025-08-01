import React, { useState } from "react";
import { useAuth } from "../providers/AuthProvider";
import "./Auth.css";

interface SignupProps {
  onSwitchToLogin: () => void;
}

const Signup: React.FC<SignupProps> = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    full_name: "",
    phone: "",
    password: "",
    confirm_password: "",
    role: "staff",
  });
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate passwords match
    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsLoading(true);

    try {
      const payload = {
        ...formData,
      };
      await register(payload);
    } catch (err: any) {
      setError(
        err.response?.data?.message || "Registration failed. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <div className="blood-icon">🩸</div>
          <h1>Blood Bank Management System</h1>
          <h2>Create Account</h2>
          <p>Join our blood bank management team</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                placeholder="Choose a username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="full_name">Full Name</label>
              <input
                type="text"
                id="full_name"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <input
              type="tel"
              id="phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              placeholder="Enter your phone number"
            />
          </div>

          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              className="role-select"
            >
              <option value="admin">
                👑 Administrator - Full system access and permissions
              </option>
              <option value="manager">
                👨‍💼 Manager - Department management and oversight
              </option>
              <option value="staff">
                👨‍⚕️ Staff Member - Blood bank operations and donor management
              </option>
              <option value="viewer">
                👁️ Viewer - Read-only access to clinical data
              </option>
            </select>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder="Create a password"
                minLength={8}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirm_password">Confirm Password</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
                placeholder="Confirm your password"
                minLength={8}
              />
            </div>
          </div>

          <button type="submit" className="auth-button" disabled={isLoading}>
            {isLoading ? "Creating Account..." : "Create Account"}
          </button>
        </form>

        <div className="test-users-section">
          <h3>Test Users Available</h3>
          <div className="test-users-grid">
            <div className="test-user-card">
              <div className="test-user-role">👑 Administrator</div>
              <div className="test-user-details">
                <p>
                  <strong>Username:</strong> admin
                </p>
                <p>
                  <strong>Password:</strong> Admin123!
                </p>
                <p>
                  <strong>Email:</strong> admin@bloodbank.com
                </p>
              </div>
            </div>
            <div className="test-user-card">
              <div className="test-user-role">👨‍💼 Manager</div>
              <div className="test-user-details">
                <p>
                  <strong>Username:</strong> manager1
                </p>
                <p>
                  <strong>Password:</strong> Manager123!
                </p>
                <p>
                  <strong>Email:</strong> manager@bloodbank.com
                </p>
              </div>
            </div>
            <div className="test-user-card">
              <div className="test-user-role">👨‍⚕️ Staff Member</div>
              <div className="test-user-details">
                <p>
                  <strong>Username:</strong> staff1
                </p>
                <p>
                  <strong>Password:</strong> Staff123!
                </p>
                <p>
                  <strong>Email:</strong> staff@bloodbank.com
                </p>
              </div>
            </div>
            <div className="test-user-card">
              <div className="test-user-role">👁️ Viewer</div>
              <div className="test-user-details">
                <p>
                  <strong>Username:</strong> viewer1
                </p>
                <p>
                  <strong>Password:</strong> Viewer123!
                </p>
                <p>
                  <strong>Email:</strong> viewer@bloodbank.com
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="auth-footer">
          <p>
            Already have an account?{" "}
            <button
              type="button"
              onClick={onSwitchToLogin}
              className="link-button"
            >
              Sign in here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
