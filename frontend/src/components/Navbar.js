import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Menu, X, Home, ShoppingBag, Info, Phone, User, LogOut, LogIn } from "lucide-react";

const Navbar = () => {
    const [user, setUser] = useState(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const storedUser = JSON.parse(localStorage.getItem("user"));
        if (storedUser) {
            setUser(storedUser);
        }

        // Detect scrolling
        const handleScroll = () => {
            if (window.scrollY > 50) {
                setIsScrolled(true);
            } else {
                setIsScrolled(false);
            }
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("user");
        setUser(null);
    };

    return (
        <nav className={`fixed top-0 left-0 w-full z-50 transition-all duration-300
            ${isScrolled ? "bg-white/50 backdrop-blur-md shadow-md" : "bg-white"} py-4 px-6 flex justify-between items-center`}>
            
            {/* Logo */}
            <Link to="/" className="text-2xl font-bold flex items-center">
                <ShoppingBag className="mr-2" size={26} />
                ShopMart
            </Link>

            {/* Mobile Menu Icon */}
            <button className="md:hidden text-black" onClick={() => setIsMenuOpen(!isMenuOpen)}>
                {isMenuOpen ? <X size={28} /> : <Menu size={28} />}
            </button>

            {/* Navigation Links (Desktop) */}
            <ul className="hidden md:flex space-x-6">
                <li><Link to="/" className="flex items-center hover:text-gray-600"><Home className="mr-2" size={20} /> Home</Link></li>
                <li><Link to="/shop" className="flex items-center hover:text-gray-600"><ShoppingBag className="mr-2" size={20} /> Shop</Link></li>
                <li><Link to="/about" className="flex items-center hover:text-gray-600"><Info className="mr-2" size={20} /> About</Link></li>
                <li><Link to="/contact" className="flex items-center hover:text-gray-600"><Phone className="mr-2" size={20} /> Contact</Link></li>
            </ul>

            {/* Mobile Menu (Hamburger) */}
            {isMenuOpen && (
                <div className="absolute top-16 left-0 w-full bg-white shadow-md md:hidden">
                    <ul className="flex flex-col space-y-4 p-4">
                        <li><Link to="/" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><Home className="mr-2" size={20} /> Home</Link></li>
                        <li><Link to="/shop" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><ShoppingBag className="mr-2" size={20} /> Shop</Link></li>
                        <li><Link to="/about" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><Info className="mr-2" size={20} /> About</Link></li>
                        <li><Link to="/contact" className="flex items-center py-2" onClick={() => setIsMenuOpen(false)}><Phone className="mr-2" size={20} /> Contact</Link></li>
                        
                    </ul>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
