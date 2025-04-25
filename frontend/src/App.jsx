import { Routes, Route } from "react-router-dom";
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import ResetRequest from "./pages/auth/ResetRequest";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/reset-password" element={<ResetRequest />} />
      {/* We'll add more routes as we create more components */}
    </Routes>
  );
}

export default App;
