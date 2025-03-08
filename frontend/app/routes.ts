import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./routes/home";
import { Welcome } from "./welcome/welcome";
import Login from "./auth/Login";
import Signup from "./auth/Signup";
import PrivateRoute from "./auth/PrivateRoute";
import { AuthProvider } from "./auth/AuthContext";

const AppRoutes: React.FC = () => (
  <AuthProvider>
    <Router>
      <Routes>
        <Route path="/" element={<Welcome />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/home" element={<PrivateRoute><Home /></PrivateRoute>} />
      </Routes>
    </Router>
  </AuthProvider>
);

export default AppRoutes;