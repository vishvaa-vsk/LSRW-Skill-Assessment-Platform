import { useState } from "react";
import { Form, Button, Alert as BootstrapAlert } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import BaseLayout from "../../components/common/BaseLayout";
import axios from "axios";

const Signup = () => {
  const [formData, setFormData] = useState({
    studName: "",
    studEmail: "",
    studClass: "",
    studRegno: "",
    studPass: "",
    studRePass: "",
  });
  const [alert, setAlert] = useState({ message: "", variant: "" });
  const [yearDeptSection, setYearDeptSection] = useState({
    year: "",
    dept: "",
    section: "",
  });
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();
  
  // Calculate password strength
  const calculatePasswordStrength = (password) => {
    if (!password) return { score: 0, label: "" };
    
    let score = 0;
    
    // Length check
    if (password.length >= 8) score += 1;
    if (password.length >= 12) score += 1;
    
    // Complexity checks
    if (/[A-Z]/.test(password)) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    // Return score and label
    const labels = ["Weak", "Fair", "Good", "Strong", "Very Strong"];
    const scoreIndex = Math.min(4, Math.floor(score / 1.5));
    
    return {
      score: scoreIndex,
      label: labels[scoreIndex]
    };
  };
  
  const passwordStrength = calculatePasswordStrength(formData.studPass);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Clear validation error when field is changed
    if(errors[name]) {
      setErrors({...errors, [name]: null});
    }
  };

  const handleYearDeptSectionChange = (e) => {
    const { id, value } = e.target;
    setYearDeptSection((prev) => ({ ...prev, [id]: value }));
    
    // Clear YDS errors when changed
    if(errors[id]) {
      setErrors({...errors, [id]: null});
    }
    
    // Clear class error when YDS fields change
    if(errors.studClass) {
      setErrors({...errors, studClass: null});
    }
  };

  const updateClassSec = () => {
    const { year, dept, section } = yearDeptSection;
    
    const newErrors = {};
    if(!year) newErrors.year = "Year is required";
    if(!dept) newErrors.dept = "Department is required";
    if(!section) newErrors.section = "Section is required";
    
    if(Object.keys(newErrors).length > 0) {
      setErrors({...errors, ...newErrors});
      return;
    }
    
    const classSec = `${year}-${dept}-${section}`;
    setFormData((prev) => ({ ...prev, studClass: classSec }));
    
    // Clear class error if it was set
    if(errors.studClass) {
      setErrors({...errors, studClass: null});
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Name validation
    if (!formData.studName) {
      newErrors.studName = "Name is required";
    } else if (!/^[A-Za-z\s.]{3,50}$/.test(formData.studName)) {
      newErrors.studName = "Name should contain only letters, spaces, and periods (3-50 characters)";
    }
    
    // Email validation
    if (!formData.studEmail) {
      newErrors.studEmail = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.studEmail)) {
      newErrors.studEmail = "Please enter a valid email address";
    }
    
    // Class validation
    if (!formData.studClass) {
      newErrors.studClass = "Please set your class using the dropdowns and update button";
    }
    
    // Registration number validation
    if (!formData.studRegno) {
      newErrors.studRegno = "Registration number is required";
    } else if (!/^[A-Za-z0-9\-]{5,15}$/.test(formData.studRegno)) {
      newErrors.studRegno = "Registration number should be 5-15 characters with only letters, numbers, and hyphens";
    }
    
    // Password validation
    if (!formData.studPass) {
      newErrors.studPass = "Password is required";
    } else if (formData.studPass.length < 8) {
      newErrors.studPass = "Password must be at least 8 characters";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.studPass)) {
      newErrors.studPass = "Password must include uppercase, lowercase, and numbers";
    }
    
    // Password confirmation
    if (!formData.studRePass) {
      newErrors.studRePass = "Please confirm your password";
    } else if (formData.studPass !== formData.studRePass) {
      newErrors.studRePass = "Passwords do not match";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return; // Stop submission if validation fails
    }

    try {
      const response = await axios.post("/api/signup", formData);
      if (response.data.success) {
        setAlert({
          message: "Registration successful!",
          variant: "success",
        });
        setTimeout(() => navigate("/"), 1500);
      }
    } catch (error) {
      setAlert({
        message:
          error.response?.data?.message ||
          "Registration failed. Please try again.",
        variant: "danger",
      });
    }
  };

  return (
    <BaseLayout>
      {alert.message && (
        <div className="container mt-2">
          <BootstrapAlert
            variant={alert.variant}
            dismissible
            onClose={() => setAlert({ message: "", variant: "" })}
            className="alert-animated py-2"
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

      <div
        className="ModelBox shadow p-3 mb-3 rounded-3"
        style={{ maxWidth: "500px", width: "90%", margin: "40px auto" }}
      >
        <h3 className="mb-3">Sign up for VEC Quiz App</h3>
        <Form onSubmit={handleSubmit} className="py-0">
          <Form.Floating className="mb-2">
            <Form.Control
              type="text"
              name="studName"
              id="floatingInput"
              placeholder="Your Name"
              required
              value={formData.studName}
              onChange={handleChange}
              isInvalid={!!errors.studName}
            />
            <label htmlFor="floatingInput">Student Name (eg: Vishvaa K)</label>
            <Form.Control.Feedback type="invalid">
              {errors.studName}
            </Form.Control.Feedback>
          </Form.Floating>

          <Form.Floating className="mb-2">
            <Form.Control
              type="email"
              name="studEmail"
              id="floatingEmail"
              placeholder="Email"
              required
              value={formData.studEmail}
              onChange={handleChange}
              isInvalid={!!errors.studEmail}
            />
            <label htmlFor="floatingEmail">Email Address</label>
            <Form.Control.Feedback type="invalid">
              {errors.studEmail}
            </Form.Control.Feedback>
          </Form.Floating>

          <div className="mb-2">
            <div className="row g-1 mb-1">
              <div className="col-4">
                <label className="form-label text-start d-block mb-1 small">Year</label>
                <select
                  className={`form-select form-select-sm ${errors.year ? "is-invalid" : ""}`}
                  id="year"
                  required
                  value={yearDeptSection.year}
                  onChange={handleYearDeptSectionChange}
                >
                  <option disabled value="">Select</option>
                  <option value="I">I</option>
                  <option value="II">II</option>
                  <option value="III">III</option>
                  <option value="IV">IV</option>
                </select>
                {errors.year && <div className="invalid-feedback">{errors.year}</div>}
              </div>
              <div className="col-4">
                <label className="form-label text-start d-block mb-1 small">Department</label>
                <select
                  className={`form-select form-select-sm ${errors.dept ? "is-invalid" : ""}`}
                  id="dept"
                  required
                  value={yearDeptSection.dept}
                  onChange={handleYearDeptSectionChange}
                >
                  <option disabled value="">Select</option>
                  <option value="CSE">CSE</option>
                  <option value="AI&DS">AI&DS</option>
                  <option value="AUTO">AUTO</option>
                  <option value="CIVIL">CIVIL</option>
                  <option value="CSE(CS)">CSE(CS)</option>
                  <option value="EEE">EEE</option>
                  <option value="ECE">ECE</option>
                  <option value="EIE">EIE</option>
                  <option value="IT">IT</option>
                  <option value="MECH">MECH</option>
                  <option value="MBA">MBA</option>
                </select>
                {errors.dept && <div className="invalid-feedback">{errors.dept}</div>}
              </div>
              <div className="col-4">
                <label className="form-label text-start d-block mb-1 small">Section</label>
                <select
                  className={`form-select form-select-sm ${errors.section ? "is-invalid" : ""}`}
                  id="section"
                  required
                  value={yearDeptSection.section}
                  onChange={handleYearDeptSectionChange}
                >
                  <option disabled value="">Select</option>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
                {errors.section && <div className="invalid-feedback">{errors.section}</div>}
              </div>
            </div>
            <div className="d-grid mt-1">
              <Button
                type="button"
                variant="warning"
                size="sm"
                style={{
                  backgroundColor: "#FFC905",
                  borderColor: "#FFC905",
                  color: "#000",
                  borderRadius: "0.25rem",
                }}
                onClick={updateClassSec}
              >
                Update
              </Button>
            </div>
          </div>

          <Form.Floating className="mb-2">
            <Form.Control
              type="text"
              style={{ textTransform: "uppercase" }}
              className="form-control"
              name="studClass"
              id="class-sec"
              placeholder="Class&Sec"
              required
              value={formData.studClass}
              onChange={handleChange}
              isInvalid={!!errors.studClass}
              readOnly
            />
            <label htmlFor="class-sec">Class & Sec</label>
            <Form.Control.Feedback type="invalid">
              {errors.studClass}
            </Form.Control.Feedback>
          </Form.Floating>

          <Form.Floating className="mb-2">
            <Form.Control
              type="text"
              name="studRegno"
              id="floatingRegNo"
              placeholder="Register Number"
              required
              value={formData.studRegno}
              onChange={handleChange}
              isInvalid={!!errors.studRegno}
            />
            <label htmlFor="floatingRegNo">Register Number</label>
            <Form.Control.Feedback type="invalid">
              {errors.studRegno}
            </Form.Control.Feedback>
          </Form.Floating>

          <Form.Floating className="mb-2">
            <Form.Control
              type="password"
              name="studPass"
              id="floatingPassword"
              placeholder="Password"
              required
              value={formData.studPass}
              onChange={handleChange}
              isInvalid={!!errors.studPass}
            />
            <label htmlFor="floatingPassword">Password</label>
            <Form.Control.Feedback type="invalid">
              {errors.studPass}
            </Form.Control.Feedback>
          </Form.Floating>
          
          <div className="password-strength mt-1 mb-2">
            <div className="d-flex justify-content-between">
              <div className="progress" style={{ height: "6px", width: "80%" }}>
                <div
                  className={`progress-bar bg-${
                    passwordStrength.score === 0 ? "danger" : 
                    passwordStrength.score === 1 ? "warning" :
                    passwordStrength.score === 2 ? "info" :
                    "success"
                  }`}
                  role="progressbar"
                  style={{ width: `${(passwordStrength.score + 1) * 20}%` }}
                  aria-valuenow={(passwordStrength.score + 1) * 20}
                  aria-valuemin="0"
                  aria-valuemax="100"
                ></div>
              </div>
              <small className={`text-${
                passwordStrength.score === 0 ? "danger" : 
                passwordStrength.score === 1 ? "warning" :
                passwordStrength.score === 2 ? "info" :
                "success"
              }`}>
                {passwordStrength.label}
              </small>
            </div>
          </div>

          <Form.Floating className="mb-2">
            <Form.Control
              type="password"
              name="studRePass"
              id="floatingConfirmPassword"
              placeholder="Confirm Password"
              required
              value={formData.studRePass}
              onChange={handleChange}
              isInvalid={!!errors.studRePass}
            />
            <label htmlFor="floatingConfirmPassword">Confirm Password</label>
            <Form.Control.Feedback type="invalid">
              {errors.studRePass}
            </Form.Control.Feedback>
          </Form.Floating>

          <Button
            type="submit"
            size="lg"
            variant="primary"
            style={{
              backgroundColor: "#0d6efd",
              borderColor: "#0d6efd",
              width: "100%",
              margin: "8px 0",
            }}
          >
            Register
          </Button>
        </Form>

        <Link to="/" className="loginLinks">
          Already have an account? Login here
        </Link>
      </div>
    </BaseLayout>
  );
};

export default Signup;
