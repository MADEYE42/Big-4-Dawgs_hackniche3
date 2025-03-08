import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Home from "./pages/Home";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Categories from "./pages/Categories";
import SDashboard from "./pages/SellerDashboard"; 
import ADashboard from "./pages/Admin"; 
import ContactUs from "./pages/ContactUs";
import AboutUs from "./pages/AboutUs";

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
    const isAuthenticated = localStorage.getItem("token");
    const userRole = localStorage.getItem("role");

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (allowedRoles && !allowedRoles.includes(userRole)) {
        return <Navigate to="/" replace />;
    }

    return children ? children : <Outlet />;
};

function App() {
    return (
        <Router>
            {/* Responsive Navbar */}
            <div className="fixed top-0 w-full z-50 bg-white shadow-md">
                <Navbar />
            </div>

            {/* Main Content */}
            <div className="mt-16 min-h-screen bg-gray-100 ">
                <Routes>
                    <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/contact" element={<ContactUs />} />
                    <Route path="/about" element={<AboutUs />} />
                    {/* Seller Dashboard (Protected) */}
                    <Route element={<ProtectedRoute allowedRoles={["seller"]} />}>
                        <Route path="/seller-dashboard" element={<SDashboard />} />
                    </Route>

                    {/* Admin Dashboard (Protected) */}
                    <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
                        <Route path="/admin-dashboard" element={<ADashboard />} />
                    </Route>

                    {/* Shop Page */}
                    <Route path="/shop" element={<ProtectedRoute><Categories /></ProtectedRoute>} />
                </Routes>
            </div>

            {/* Responsive Footer */}
            <div className="w-full bg-gray-900 text-white text-center py-4">
                <Footer />
            </div>
        </Router>
    );
}

export default App;
