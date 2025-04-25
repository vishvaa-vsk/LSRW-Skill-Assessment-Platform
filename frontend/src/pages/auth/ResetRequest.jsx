import { useState } from "react";
import { Form, Button, Alert as BootstrapAlert } from "react-bootstrap";
import { Link } from "react-router-dom";
import BaseLayout from "../../components/common/BaseLayout";
import axios from "axios";

const ResetRequest = () => {
  const [email, setEmail] = useState("");
  const [alert, setAlert] = useState({ message: "", variant: "" });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("/api/reset-request", { email });
      if (response.data.success) {
        setAlert({
          message:
            "A link has been sent to your email for password reset! Click that to reset your password.",
          variant: "success",
        });
        setEmail("");
      }
    } catch (error) {
      setAlert({
        message:
          error.response?.data?.message ||
          "Failed to process your request. Please try again.",
        variant: "danger",
      });
    }
  };

  return (
    <BaseLayout>
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
        <h3>Reset Your Password</h3>
        <p>
          Enter your email address and we'll send you a link to reset your
          password.
        </p>

        <Form onSubmit={handleSubmit}>
          <Form.Floating className="mb-3">
            <Form.Control
              type="email"
              id="resetEmail"
              name="resetEmail"
              placeholder="Email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <label htmlFor="resetEmail">Email Address</label>
          </Form.Floating>

          <Button type="submit" size="lg" variant="primary">
            Send Reset Link
          </Button>
        </Form>

        <Link to="/" className="loginLinks">
          Back to Login
        </Link>
      </div>
    </BaseLayout>
  );
};

export default ResetRequest;
