import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
    const [user, setUser] = useState(null);

    useEffect(() => {
        // Simulating user data from localStorage or API
        const storedUser = JSON.parse(localStorage.getItem("user"));
        if (storedUser) {
            setUser(storedUser);
        }
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("user");
        setUser(null);
    };

    return (
        <nav className="bg-white font-[Poppins] text-black shadow-md py-4 px-6 flex justify-between items-center">
            {/* Logo */}
            <Link to="/" className="text-2xl font-bold">ShopMart</Link>

            {/* Navigation Links */}
            <ul className="flex space-x-6">
                <li><Link to="/" className="hover:text-gray-600">Home</Link></li>
                <li><Link to="/shop" className="hover:text-gray-600">Shop</Link></li>
                <li><Link to="/about" className="hover:text-gray-600">About</Link></li>
                <li><Link to="/contact" className="hover:text-gray-600">Contact</Link></li>
            </ul>

            {/* User Section */}
            <div className="relative">
                {user ? (
                    <div className="flex items-center space-x-4">
                        {/* Avatar with initials */}
                        <div className="w-10 h-10 bg-gray-300 text-black font-semibold flex items-center justify-center rounded-full cursor-pointer">
                            {user.name[0].toUpperCase()}{user.surname[0].toUpperCase()}
                        </div>

                        {/* Dropdown Menu */}
                        <div className="absolute right-0 mt-2 w-48 bg-white shadow-lg rounded-lg p-2 hidden group-hover:block">
                            <Link to="/profile" className="block px-4 py-2 hover:bg-gray-100">Profile</Link>
                            <button onClick={handleLogout} className="block px-4 py-2 text-red-600 hover:bg-gray-100 w-full text-left">
                                Logout
                            </button>
                        </div>
                    </div>
                ) : (
                    <Link to="/login" className="bg-white text-black px-5 py-2 rounded-lg border border-gray-400 hover:bg-gray-200 transition">
                        Login
                    </Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
