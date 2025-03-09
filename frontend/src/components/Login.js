import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

const Login = () => {
    const [form, setForm] = useState({ email: "", password: "", role: "" });
    const [error, setError] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        try {
            const response = await fetch('http://localhost:3000/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(form),
            });

            const res = await response.json();

            if (response.ok) {

                if (res.role === "customer") navigate("/home");
                else if (res.role === "admin") navigate("/admin-dashboard");
                else navigate("/seller-dashboard");
            } else {
                setError(res.message || "Login failed. Please try again.");
            }
        } catch (err) {
            console.error("Login error:", err);
            setError("Network error. Please try again.");
        }
    };

    return (
        <div className="font-[Poppins] flex items-center justify-center h-screen bg-gray-900">
            <div className="w-full max-w-md bg-white backdrop-blur-lg p-8 rounded-xl shadow-lg border border-gray-700">
                <div className="flex justify-center mb-6">
                    <img src="/logo.png" alt="Logo" className="h-8" />
                </div>

                <h2 className="text-2xl font-semibold text-black text-center mb-2">Welcome back!</h2>
                <p className="text-gray-600 text-center mb-6">
                    Don't have an account?{" "}
                    <a href="/register" className="text-blue-500 font-medium">Sign up</a>
                </p>

                {error && (
                    <div className="bg-red-100 text-red-600 p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {/* Email Input */}
                    <div>
                        <label className="block text-gray-600 text-sm font-medium mb-1">Email address</label>
                        <input
                            type="email"
                            name="email"
                            className="w-full border border-gray-500 bg-transparent text-white p-3 rounded-lg focus:ring-2 focus:ring-blue-500 placeholder-gray-400"
                            placeholder="Enter your email"
                            value={form.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    {/* Password Input */}
                    <div className="relative">
                        <label className="block text-gray-600 text-sm font-medium mb-1">Password</label>
                        <input
                            type={showPassword ? "text" : "password"}
                            name="password"
                            className="w-full border border-gray-500 bg-transparent text-white p-3 rounded-lg focus:ring-2 focus:ring-blue-500 placeholder-gray-400 pr-10"
                            placeholder="Enter your password"
                            value={form.password}
                            onChange={handleChange}
                            required
                        />
                        <span
                            className="absolute top-10 right-3 text-gray-400 cursor-pointer"
                            onClick={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? <FaEyeSlash /> : <FaEye />}
                        </span>
                    </div>

                    {/* Role Selection Dropdown */}
                    <div>
                        <label className="block text-gray-600 text-sm font-medium mb-1">Select Role</label>
                        <select
                            name="role"
                            className="w-full border border-gray-500 bg-transparent text-black p-3 rounded-lg focus:ring-2 focus:ring-blue-500"
                            value={form.role}
                            onChange={handleChange}
                            required
                        >
                            <option value="" disabled>Select your role</option>
                            <option value="customer">Customer</option>
                            <option value="seller">Seller</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        className="w-full bg-white text-black p-3 rounded-lg font-semibold hover:bg-gray-300 transition duration-300 border border-black"
                    >
                        Log in
                    </button>
                </form>

                <div className="text-center my-4 text-gray-500">OR</div>

                {/* Google Login Button */}
                <button className="w-full border border-gray-500 hover:text-white p-3 rounded-lg font-medium hover:bg-gray-700 text-black transition duration-300 flex justify-center items-center">
                    <img src="/google-icon.png" alt="Google" className="h-5 w-5 mr-2" />
                    Log in with Google
                </button>

                <p className="text-gray-500 text-center text-sm mt-4">
                    By logging in, you agree to our <a href="#" className="text-blue-500">Terms of Service</a> and <a href="#" className="text-blue-500">Privacy Policy</a>.
                </p>
            </div>
        </div>
    );
};

export default Login;