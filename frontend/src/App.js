import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Home from "./pages/Home";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Categories from "./pages/Categories";
import Dashboard from "./pages/Dashboard"; // Import Dashboard if not already imported

function ProtectedRoute({ children, allowedRoles }) {
    const isAuthenticated = localStorage.getItem("token");
    const userRole = localStorage.getItem("role");
    console.log(userRole);
    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(userRole)) {
        return <Navigate to="/" replace />;
    }

    return children ? children : <Outlet />;
}

function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                {/* Protected Route for Seller/Admin */}
                <Route element={<ProtectedRoute allowedRoles={["seller", "admin"]} />}>
                    <Route path="/dashboard" element={<Dashboard />} />
                </Route>

                <Route path="/shop" element={<ProtectedRoute><Categories /></ProtectedRoute>} />
            </Routes>
            <Footer />
        </Router>
    );
}

export default App;
