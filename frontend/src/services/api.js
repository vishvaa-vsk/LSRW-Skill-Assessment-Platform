import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add authentication token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("authToken");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Auth services
export const authService = {
  login: (credentials) => api.post("/api/login", credentials),
  signup: (userData) => api.post("/api/signup", userData),
  resetPasswordRequest: (email) => api.post("/api/reset-request", { email }),
  resetPassword: (userId, password) =>
    api.post(`/api/password-reset/${userId}`, { password }),
};

// User services
export const userService = {
  getProfile: () => api.get("/api/profile"),
  updateProfile: (data) => api.put("/api/profile", data),
};

// Quiz services
export const quizService = {
  getQuiz: (testCode) => api.get(`/api/quiz/${testCode}`),
  submitQuiz: (testCode, answers) =>
    api.post(`/api/quiz/${testCode}/submit`, { answers }),
};

export default api;
