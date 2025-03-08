import React from "react";

const Home = () => {
    return (
        <div className="bg-gray-100 min-h-screen font-[Poppins]">
            
            <header className="text-center py-12">
                <h1 className="text-5xl font-bold text-gray-900">
                    The Best Way to Shop for Products You Love
                </h1>
                <p className="text-gray-600 mt-4 text-lg">
                    Discover the latest trends and exclusive deals
                </p>
            </header>
            
            <section className="grid grid-cols-4 gap-4 px-12">
                {['Electronics', 'Fashion', 'Home & Kitchen', 'Beauty'].map((category, index) => (
                    <div key={index} className="text-center p-4 bg-white rounded-lg shadow-md">
                        <img src={`/images/${category.toLowerCase()}.png`} alt={category} className="w-24 mx-auto" />
                        <h2 className="mt-2 text-lg font-semibold">{category}</h2>
                    </div>
                ))}
            </section>

            <section className="px-12 py-8">
                <h2 className="text-3xl font-bold mb-6">Featured Products</h2>
                <div className="grid grid-cols-3 gap-6">
                    {[1, 2, 3].map((product) => (
                        <div key={product} className="bg-white p-6 rounded-lg shadow-lg">
                            <img src="/images/sample-product.jpg" alt="Product" className="w-full h-48 object-cover rounded-md" />
                            <h3 className="text-xl font-semibold mt-4">Product Name</h3>
                            <p className="text-gray-600">Short product description.</p>
                            <p className="text-xl font-bold mt-2">$199.99</p>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export default Home;