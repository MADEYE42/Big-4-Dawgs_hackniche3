import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";

const ProductDetails = () => {
    const { asin } = useParams();
    const [product, setProduct] = useState(null);
    const [featuredProducts, setFeaturedProducts] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!asin) {
            setError("Invalid product ID");
            setLoading(false);
            return;
        }

        const fetchProduct = async () => {
            try {
                const response = await fetch("http://localhost:3000/view-product", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ asin })
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error || "Failed to fetch");

                setProduct(data);

            } catch (err) {
                console.error("Error fetching product:", err);
                setError(err.message);
            }
        };

        const fetchFeaturedProducts = async () => {
            try {
                const response = await fetch(`http://localhost:8000/recommendations/asin/${asin}?top_n=9`);
                if (!response.ok) {
                    throw new Error("Failed to fetch featured products");
                }
                const data = await response.json();
                setFeaturedProducts(data);

            } catch (error) {
                console.error("Error fetching featured products:", error);
                setError(error.message);
            }
        };

        Promise.all([fetchProduct(), fetchFeaturedProducts()])
            .finally(() => setLoading(false));
    }, [asin]);


    if (loading) return <p className="text-gray-500 text-center text-lg mt-6">Loading...</p>;
    if (error) return <p className="text-red-500 text-center text-lg mt-6">{error}</p>;

    return (
        <div className="max-w-6xl mx-auto my-10 px-6">
            {/* Product Details Section */}
            <div className="max-w-3xl mx-auto p-6 bg-white shadow-lg rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <img
                        src={product.image_url || "/fallback-image.jpg"}
                        alt={product.title}
                        className="w-full h-80 object-cover rounded-lg shadow-md"
                    />
                    <div className="flex flex-col justify-center">
                        <h2 className="text-3xl font-bold text-gray-900">{product.title}</h2>
                        <p className="text-gray-600 text-lg mt-2">{product.category}</p>
                        <p className="text-2xl font-semibold text-green-600 mt-4">₹ {product.price}</p>
                        <button className="mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-semibold hover:bg-blue-700 transition">
                            Add to Cart
                        </button>
                    </div>
                </div>
            </div>

            {/* Featured Products Section */}
            <section className="py-12">
                <h2 className="text-3xl font-bold text-center mb-8 text-gray-900">Recommended Products</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                    {featuredProducts.map((featuredProduct) => (
                        <Link key={featuredProduct.asin} to={`/product/${featuredProduct.asin}`}>
                            <div className="bg-gray-50 p-6 rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition duration-300">
                                <img
                                    src={featuredProduct.image_url || "/images/sample-product.jpg"}
                                    alt={featuredProduct.title}
                                    className="w-full h-52 object-cover rounded-md"
                                />
                                <h3 className="text-xl font-semibold mt-4">
                                    {featuredProduct.title.length > 50
                                        ? featuredProduct.title.substring(0, 80) + "..."
                                        : featuredProduct.title}
                                </h3>
                                <p className="text-gray-600">{featuredProduct.category}</p>
                                <p className="text-xl font-bold mt-2 text-gray-900">₹ {featuredProduct.price}</p>
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

export default ProductDetails;