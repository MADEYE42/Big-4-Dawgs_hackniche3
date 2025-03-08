import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Register";
import Home from "./pages/Home";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Categories from "./pages/Categories";

function ProtectedRoute({ children }) {
    const isAuthenticated = localStorage.getItem("token"); 
    return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/shop" element={<Categories />} />

            </Routes>
            <Footer/>
        </Router>
    );
}

export default App;
