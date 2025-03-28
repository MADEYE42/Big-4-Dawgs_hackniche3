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

    const handleLoyaltyPress = async () => {


        try {
            const response = await fetch('https://a985-14-139-125-227.ngrok-free.app/loyalty/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "user": {
                        "user_id": user.user_id || "user123", // Use user_id from localStorage or fallback
                        "lifetime_purchases": 2,
                        "reviews_written": 2,
                        "challenge_progress": 3
                    },
                    "num_recommendations": 3
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            console.log("Loyalty Recommendations:", data);

        } catch (error) {
            console.error("Error fetching loyalty recommendations:", error);
        }
    };

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
                <li>
                    <button
                        onClick={handleLoyaltyPress}
                        className="flex items-center hover:text-gray-600"
                    >
                        <Home className="mr-2" size={20} />
                        Loyalty
                    </button>
                </li>
                <li><Link to="/" className="flex items-center hover:text-gray-600"><Home className="mr-2" size={20} /> Home</Link></li>
                <li><Link to="/shop" className="flex items-center hover:text-gray-600"><ShoppingBag className="mr-2" size={20} /> Shop</Link></li>
                <li><Link to="/about" className="flex items-center hover:text-gray-600"><Info className="mr-2" size={20} /> About</Link></li>
                <li><Link to="/contact" className="flex items-center hover:text-gray-600"><Phone className="mr-2" size={20} /> Contact</Link></li>
                {user ? (
                    <>
                        <li><Link to="/profile" className="flex items-center hover:text-gray-600"><User className="mr-2" size={20} /> Profile</Link></li>
                        <li>
                            <button onClick={handleLogout} className="flex items-center hover:text-gray-600">
                                <LogOut className="mr-2" size={20} /> Log Out
                            </button>
                        </li>
                    </>
                ) : (
                    <li><Link to="/login" className="flex items-center hover:text-gray-600"><LogIn className="mr-2" size={20} /> Log In</Link></li>
                )}
            </ul>

            {/* Mobile Menu (Hamburger) */}
            {isMenuOpen && (
                <div className="absolute top-16 left-0 w-full bg-white shadow-md md:hidden">
                    <ul className="flex flex-col space-y-4 p-4">
                        <li>
                            <button
                                onClick={() => {
                                    handleLoyaltyPress();
                                    setIsMenuOpen(false);
                                }}
                                className="flex items-center py-2 border-b w-full text-left"
                            >
                                <Home className="mr-2" size={20} />
                                Loyalty
                            </button>
                        </li>
                        <li><Link to="/" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><Home className="mr-2" size={20} /> Home</Link></li>
                        <li><Link to="/shop" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><ShoppingBag className="mr-2" size={20} /> Shop</Link></li>
                        <li><Link to="/about" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><Info className="mr-2" size={20} /> About</Link></li>
                        <li><Link to="/contact" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><Phone className="mr-2" size={20} /> Contact</Link></li>
                        {user ? (
                            <>
                                <li><Link to="/profile" className="flex items-center py-2 border-b" onClick={() => setIsMenuOpen(false)}><User className="mr-2" size={20} /> Profile</Link></li>
                                <li>
                                    <button onClick={() => { handleLogout(); setIsMenuOpen(false); }} className="flex items-center py-2 w-full text-left">
                                        <LogOut className="mr-2" size={20} /> Log Out
                                    </button>
                                </li>
                            </>
                        ) : (
                            <li><Link to="/login" className="flex items-center py-2" onClick={() => setIsMenuOpen(false)}><LogIn className="mr-2" size={20} /> Log In</Link></li>
                        )}
                    </ul>
                </div>
            )}
        </nav>
    );
};

export default Navbar;