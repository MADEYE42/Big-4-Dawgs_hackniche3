import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
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
                    {[
                        { name: 'Electronics', img: '/images/electronics.png' },
                        { name: 'Fashion', img: '/images/fashion.png' },
                        { name: 'Home & Kitchen', img: '/images/home-kitchen.png' },
                        { name: 'Beauty', img: '/images/beauty.png' }
                    ].map((category, index) => (
                        <div 
                            key={index} 
                            className="text-center p-6 bg-white rounded-lg shadow-md hover:shadow-xl transform hover:scale-105 transition duration-300"
                        >
                            <img src={category.img} alt={category.name} className="w-24 h-24 mx-auto" />
                            <h2 className="mt-3 text-xl font-semibold">{category.name}</h2>
                        </div>
                    ))}
                </div>
            </section>

            {/* Featured Products Section */}
            <section className="px-6 md:px-16 py-12 bg-white">
                <h2 className="text-3xl font-bold text-center mb-8 text-gray-900">Featured Products</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map((product) => (
                        <div 
                            key={product} 
                            className="bg-gray-50 p-6 rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition duration-300"
                        >
                            <img src="/images/sample-product.jpg" alt="Product" className="w-full h-52 object-cover rounded-md" />
                            <h3 className="text-xl font-semibold mt-4">Stylish Product</h3>
                            <p className="text-gray-600">Premium quality at a great price.</p>
                            <p className="text-xl font-bold mt-2 text-gray-900">$199.99</p>
                            <button className="mt-4 bg-black text-white px-5 py-2 rounded-md font-semibold shadow-md hover:bg-gray-800 transition">
                                Buy Now
                            </button>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="bg-gray-900 text-white text-center py-16 px-6">
                <h2 className="text-3xl md:text-4xl font-bold">Sign Up for Exclusive Offers!</h2>
                <p className="text-lg text-gray-300 mt-3">Be the first to get the best deals.</p>
                <div className="mt-6 flex flex-col md:flex-row items-center justify-center">
                    <input 
                        type="email" 
                        placeholder="Enter your email" 
                        className="w-full md:w-72 p-3 rounded-md text-gray-900 focus:outline-none"
                    />
                    <button className="mt-3 md:mt-0 md:ml-2 bg-gray-800 text-white px-6 py-3 rounded-md hover:bg-black transition">
                        Subscribe
                    </button>
                </div>
            </section>            
        </div>
    );
};

export default Home;
