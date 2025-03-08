import React, { useState } from "react";
import { register } from "../utils/api";
import { useNavigate } from "react-router-dom";

const Register = () => {
    const [form, setForm] = useState({ name: "", email: "", password: "" });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        try {
            await register(form);
            navigate("/login");
        } catch (err) {
            setError(err.response?.data?.error || "Registration failed. Please try again.");
        }
    };

    return (
        <div className="flex h-screen">
            {/* Left Side - Form */}
            <div className="w-1/2 flex flex-col justify-center items-center bg-white p-12">
                <div className="w-full max-w-md">
                    <div className="flex justify-center mb-6">
                        <img src="/logo.png" alt="Logo" className="h-10" />
                    </div>

                    <h2 className="text-2xl font-semibold text-gray-900 text-center mb-2">Create an account</h2>
                    <p className="text-gray-500 text-center mb-6">
                        Already have an account?{" "}
                        <a href="/login" className="text-black font-medium">Log in</a>
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
                            <label className="block text-gray-700 text-sm font-medium mb-1">Email address</label>
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

                        <button
                            type="submit"
                            className="w-full bg-black text-white p-3 rounded-lg font-semibold hover:bg-black transition duration-300"
                        >
                            Sign up
                        </button>
                    </form>

                    <div className="text-center my-4 text-gray-500">OR</div>
                    
                    <button className="w-full border border-gray-300 text-gray-700 p-3 rounded-lg font-medium hover:bg-gray-100 transition duration-300">
                        Sign up with SSO
                    </button>
                </div>
            </div>

            {/* Right Side - Design Pattern */}
            <div className="w-1/2 bg-black flex items-center justify-center">
                <div className="grid grid-cols-3 gap-2">
                    {Array(9).fill(null).map((_, i) => (
                        <div key={i} className="w-16 h-16 bg-black rounded-br-full"></div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Register;
