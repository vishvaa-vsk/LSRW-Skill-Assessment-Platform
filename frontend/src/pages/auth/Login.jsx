import { useState } from "react";
import { Form, Button, Alert as BootstrapAlert } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import BaseLayout from "../../components/common/BaseLayout";
import axios from "axios";

const Login = () => {
  const [formData, setFormData] = useState({
    studRegno: "",
    studPass: "",
  });
  const [alert, setAlert] = useState({ message: "", variant: "" });
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("/api/login", formData);
      if (response.data.success) {
        // Show success message before redirecting
        setAlert({
          message: "Login successful! Redirecting to dashboard...",
          variant: "success",
        });
        setTimeout(() => navigate("/dashboard"), 1500);
      }
    } catch (error) {
      setAlert({
        message:
          error.response?.data?.message || "Login failed. Please try again.",
        variant: "danger",
      });
    }
  };

  return (
    <BaseLayout>
      {/* Alert positioned above the form */}
      {alert.message && (
        <div className="container mt-4">
          <BootstrapAlert
            variant={alert.variant}
            dismissible
            onClose={() => setAlert({ message: "", variant: "" })}
            className="alert-animated"
          >
            {alert.variant === "success" && (
              <i className="fas fa-check-circle me-2"></i>
            )}
            {alert.variant === "danger" && (
              <i className="fas fa-exclamation-circle me-2"></i>
            )}
            {alert.message}
          </BootstrapAlert>
        </div>
      )}

      <div className="ModelBox shadow-lg p-3 mb-5 rounded-3">
        <h3>Student Login</h3>

        <Form onSubmit={handleSubmit}>
          <Form.Floating className="mb-3">
            <Form.Control
              type="text"
              name="studRegno"
              id="floatingInput"
              placeholder="Student Registration No"
              required
              autoComplete="off"
              value={formData.studRegno}
              onChange={handleChange}
            />
            <label htmlFor="floatingInput">Student Registration No</label>
          </Form.Floating>

          <Form.Floating className="mb-3 password-field-container">
            <Form.Control
              type={showPassword ? "text" : "password"}
              name="studPass"
              id="floatingPassword"
              placeholder="Password"
              required
              autoComplete="off"
              value={formData.studPass}
              onChange={handleChange}
            />
            <label htmlFor="floatingPassword">Password</label>
            <span
              className="password-toggle-icon"
              onClick={togglePasswordVisibility}
            >
              <i
                className={showPassword ? "far fa-eye-slash" : "far fa-eye"}
              ></i>
            </span>
          </Form.Floating>

          <Button type="submit" size="lg" variant="success">
            Login
          </Button>
        </Form>

        <a href="/signup" className="loginLinks">
          Don't have an account? Sign up here
        </a>
        <a href="/reset-password" className="loginLinks">
          Forgot your password?
        </a>
      </div>
    </BaseLayout>
  );
};

export default Login;
