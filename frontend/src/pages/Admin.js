import React, { useEffect, useState } from "react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";
import data from "../data/Admin.json";

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#a4de6c", "#d0ed57"];

const AdminDashboard = () => {
  const [pieData, setPieData] = useState([]);
  const [barData, setBarData] = useState([]);

  useEffect(() => {
    const productSales = [];
    const sellerSales = {};
    
    data.forEach(seller => {
      seller.products.forEach(product => {
        productSales.push({ name: product.item, value: product.revenue });
        
        if (sellerSales[seller.seller_name]) {
          sellerSales[seller.seller_name] += product.sales;
        } else {
          sellerSales[seller.seller_name] = product.sales;
        }
      });
    });

    setPieData(productSales);
    setBarData(Object.keys(sellerSales).map(name => ({ name, sales: sellerSales[name] })));
  }, []);

  return (
    <div className="p-6 min-h-screen bg-gray-100 text-black">
      <h1 className="text-3xl font-bold mb-6 text-center">Admin Dashboard</h1>

      {/* Pie Chart Section */}
      <div className="bg-white p-6 shadow-lg rounded-xl flex flex-col lg:flex-row items-center lg:justify-between">
        <div className="lg:w-1/3 w-full text-center lg:text-left">
          <h2 className="text-xl font-semibold mb-4">Revenue Contribution by Item</h2>
          <Legend />
        </div>
        <div className="lg:w-2/3 w-full flex justify-center">
          <PieChart width={350} height={300}>
            <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={120} label>
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </div>
      </div>

      {/* Bar Chart Section */}
      <div className="bg-white p-6 shadow-lg rounded-xl mt-6">
        <h2 className="text-xl font-semibold mb-4 text-center">Top Selling Sellers</h2>
        <div className="flex justify-center">
          <BarChart width={window.innerWidth < 768 ? 300 : 600} height={300} data={barData}>
            <XAxis dataKey="name" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="sales" fill="#82ca9d" />
          </BarChart>
        </div>
      </div>

      {/* Table Section */}
      <div className="mt-6 bg-white p-6 shadow-lg rounded-xl overflow-x-auto">
        <h2 className="text-xl font-semibold mb-4 text-center">Product Details</h2>
        <table className="w-full border-collapse border border-gray-300 text-left">
          <thead className="bg-gray-200">
            <tr>
              <th className="border p-2">Item</th>
              <th className="border p-2">Price</th>
              <th className="border p-2">Sales</th>
              <th className="border p-2">Revenue</th>
              <th className="border p-2">Stock Remaining</th>
              <th className="border p-2">Rating</th>
              <th className="border p-2">Suggestion</th>
            </tr>
          </thead>
          <tbody>
            {data.map((seller, i) =>
              seller.products.map((product, j) => (
                <tr key={`${i}-${j}`} className="border hover:bg-gray-100">
                  <td className="border p-2">{product.item}</td>
                  <td className="border p-2">${product.price}</td>
                  <td className="border p-2">{product.sales}</td>
                  <td className="border p-2">${product.revenue.toFixed(2)}</td>
                  <td className="border p-2">{product.stock_remaining}</td>
                  <td className="border p-2">{product.rating} ⭐</td>
                  <td className="border p-2">
                    {product.sales < 100 && product.revenue < 5000 ? (
                      <span className="text-red-600">Consider adding discounts</span>
                    ) : product.sales > 200 ? (
                      <span className="text-green-600">Bring more similar items</span>
                    ) : (
                      <span className="text-gray-600">Stable</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;
