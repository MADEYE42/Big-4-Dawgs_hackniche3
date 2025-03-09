import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const Home = () => {
    const [categories, setCategories] = useState([]);
    const [featuredProducts, setFeaturedProducts] = useState([]);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const response = await fetch("http://localhost:3000/home");
                if (response.ok) {
                    const data = await response.json();
                    setCategories(data);
                } else {
                    console.error("Failed to fetch categories");
                }
            } catch (error) {
                console.error("Error fetching categories:", error);
            }
        };

        const fetchFeaturedProducts = async () => {
            try {
                const response = await fetch("http://localhost:3000/init_suggestion");
                if (response.ok) {
                    const data = await response.json();
                    setFeaturedProducts(data);
                    console.log(data)
                } else {
                    console.error("Failed to fetch featured products");
                }
            } catch (error) {
                console.error("Error fetching featured products:", error);
            }
        };

        fetchCategories();
        fetchFeaturedProducts();
    }, []);

    return (
        <div className="bg-gray-100 min-h-screen font-[Poppins]">
            {/* Hero Section */}
            <header className="text-center py-20 px-6 bg-white shadow-md">
                <h1 className="text-4xl md:text-6xl font-extrabold text-gray-900 leading-tight">
                    Elevate Your Shopping Experience
                </h1>
                <p className="text-gray-600 mt-4 text-lg md:text-xl">
                    Discover exclusive deals & latest trends at unbeatable prices!
                </p>
                <Link to="/shop">
                    <button className="mt-6 bg-black text-white px-8 py-3 rounded-full text-lg font-semibold shadow-lg hover:bg-gray-800 transition">
                        Start Shopping
                    </button>
                </Link>
            </header>

            {/* Categories Section */}
            <section className="px-6 md:px-16 py-12 bg-gray-900">
                <h2 className="text-3xl font-bold text-center mb-8 text-white">Shop by Categories</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    {categories.map((category, index) => (
                        <div
                            key={index}
                            className="text-center p-6 bg-white rounded-lg shadow-md hover:shadow-xl transform hover:scale-105 transition duration-300"
                        >
                            <img src="/images/default-category.png" alt={category.category} className="w-24 h-24 mx-auto" />
                            <h2 className="mt-3 text-xl font-semibold">{category.category}</h2>
                        </div>
                    ))}
                </div>
            </section>

            {/* Featured Products Section */}
            <section className="px-6 md:px-16 py-12 bg-white">
                <h2 className="text-3xl font-bold text-center mb-8 text-gray-900">Featured Products</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                    {featuredProducts.map((product, index) => (
                        <Link to={`/product/${product.asin}`}>
                            <div className="bg-gray-50 p-6 rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition duration-300">
                                <img src={product.image_url} alt="Product" className="w-full h-52 object-cover rounded-md" />
                                <h3 className="text-xl font-semibold mt-4">
                                    {product.title.length > 50 ? product.title.substring(0, 80) + "..." : product.title}
                                </h3>
                                <p className="text-gray-600">{product.category}</p>
                                <p className="text-xl font-bold mt-2 text-gray-900">₹ {product.price}</p>

                                {/* View Product Button */}
                                <button className="mt-4 bg-black text-white px-5 py-2 rounded-md font-semibold shadow-md hover:bg-gray-800 transition">
                                    View Product
                                </button>
                            </div>
                        </Link>

                    ))}
                </div>
            </section>
        </div>
    );
};

export default Home;