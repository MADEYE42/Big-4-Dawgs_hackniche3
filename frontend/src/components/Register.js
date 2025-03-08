import React, { useState } from "react";
import { register } from "../utils/api";
import { useNavigate } from "react-router-dom";
import { FaGoogle } from "react-icons/fa";

const Register = () => {
    const [form, setForm] = useState({ name: "", email: "", password: "", role: "" });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((prevForm) => ({
            ...prevForm,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        try {
            if (!form.role) {
                setError("Please select a role.");
                return;
            }

            await register(form);
            navigate("/login");
        } catch (err) {
            setError(err.response?.data?.error || "Registration failed. Please try again.");
        }
    };

    return (
        <div className="flex flex-col md:flex-row h-screen font-poppins">
            {/* Left Side - Form */}
            <div className="w-full md:w-1/2 flex flex-col justify-center items-center bg-white p-6 md:p-12">
                <div className="w-full max-w-md">
                    <div className="flex justify-center mb-6">
                        <img src="/logo.png" alt="Logo" className="h-12" />
                    </div>

                    <h2 className="text-3xl font-bold text-gray-900 text-center mb-2">Join ShopMart</h2>
                    <p className="text-gray-500 text-center mb-6">
                        Already have an account? <a href="/login" className="text-black font-medium">Log in</a>
                    </p>

                    {error && (
                        <div className="bg-red-100 text-red-600 p-3 rounded mb-4 text-sm">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-gray-700 text-sm font-medium mb-1">Full Name</label>
                            <input
                                type="text"
                                name="name"
                                className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-black"
                                placeholder="Enter your full name"
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-gray-700 text-sm font-medium mb-1">Email Address</label>
                            <input
                                type="email"
                                name="email"
                                className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-black"
                                placeholder="Enter your email"
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-gray-700 text-sm font-medium mb-1">Password</label>
                            <input
                                type="password"
                                name="password"
                                className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-black"
                                placeholder="Create a password"
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-gray-700 text-sm font-medium mb-1">Select Role</label>
                            <select
                                name="role"
                                className="w-full border border-gray-300 p-3 rounded-lg focus:ring-2 focus:ring-black"
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

                        <button
                            type="submit"
                            className="w-full bg-black text-white p-3 rounded-lg font-semibold hover:bg-gray-800 transition duration-300"
                        >
                            Sign up
                        </button>
                    </form>

                    <div className="text-center my-4 text-gray-500">OR</div>
                    
                    <button className="w-full border border-gray-300 text-gray-700 p-3 rounded-lg font-medium flex items-center justify-center gap-2 hover:bg-gray-100 transition duration-300">
                        <FaGoogle className="text-red-500" /> Sign up with Google
                    </button>
                </div>
            </div>

            {/* Right Side - E-Commerce Banner */}
            <div className="hidden md:flex w-1/2 bg-gradient-to-r from-black to-gray-800 items-center justify-center">
                <div className="text-center text-white px-8">
                    <h2 className="text-4xl font-bold mb-4">Start Your Shopping Journey</h2>
                    <p className="text-lg text-gray-300 mb-6">Join ShopMart and explore thousands of amazing products at unbeatable prices.</p>
                    <div className="grid grid-cols-3 gap-3">
                        {Array(9).fill(null).map((_, i) => (
                            <div key={i} className="w-16 h-16 bg-white opacity-20 rounded-lg"></div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Register;