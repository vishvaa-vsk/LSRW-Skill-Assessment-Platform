import { Routes, Route } from "react-router-dom";
import Login from "./pages/auth/Login";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      {/* We'll add more routes as we create more components */}
    </Routes>
  );
}

export default App;
