import React, { useEffect, useState } from "react";
import axios from "axios";

const Categories = () => {
  const [products, setProducts] = useState([]);
  const [recommendedProduct, setRecommendedProduct] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get("/data/products.json");
        setProducts(response.data);
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    };

    const fetchRecommendedProduct = async () => {
      try {
        const response = await axios.get("/api/recommendation"); // Fetch from ML backend
        setRecommendedProduct(response.data);
      } catch (error) {
        console.error("Error fetching recommended product:", error);
      }
    };

    fetchProducts();
    fetchRecommendedProduct();
  }, []);
  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Categories</h1>

      {/* Recommended Product Section */}
      {recommendedProduct && (
        <div className="mb-8 p-4 bg-white shadow rounded-lg">
          <h2 className="text-xl font-semibold">Recommended for You</h2>
          <div className="mt-4">
            <img
              src={recommendedProduct.image}
              alt={recommendedProduct.name}
              className="w-32 h-32 object-cover rounded"
            />
            <h3 className="text-lg font-medium mt-2">{recommendedProduct.name}</h3>
            <p className="text-gray-600">{recommendedProduct.description}</p>
            <p className="text-lg font-bold mt-1">${recommendedProduct.price}</p>
          </div>
        </div>
      )}

      {/* Products Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6" >
        {products.map((product) => (
          <div
            key={product.id}
            className="p-4 bg-white shadow rounded-lg text-center hover:shadow-lg transition cursor-pointer"
            onClick={() => console.log(product.subcategory)}
          >
            <img
              src={product.image}
              alt={product.name}
              className="w-full h-40 object-cover rounded-t-lg"
            />
            <h3 className="text-lg font-semibold mt-2">{product.name}</h3>
            <p className="text-gray-600">{product.category}</p>
            <p className="text-lg font-bold mt-1">${product.price}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Categories;
