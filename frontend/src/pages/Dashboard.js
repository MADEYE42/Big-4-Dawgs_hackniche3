import React, { useEffect, useState } from "react";
import { PieChart, Pie, Tooltip, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from "recharts";
import data from "../data/Seller.json";
import { Card } from "../components/ui/card";
import { Table, TableHeader, TableBody, TableRow, TableCell } from "../components/ui/table";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#A569BD", "#E74C3C", "#16A085", "#2ECC71", "#F1C40F", "#E67E22"];

const Dashboard = () => {
  const [chartData, setChartData] = useState([]);
  const [barData, setBarData] = useState([]);

  useEffect(() => {
    setChartData(data.map(item => ({ name: item.item, value: item.sales })));
    setBarData(data.map(item => ({ name: item.item, stock: item.stock_remaining })));
  }, []);

  return (
    <div className="bg-white text-black p-8 min-h-screen font-[Poppins]">
      <h1 className="text-3xl font-bold mb-6 text-center">📊 Seller Dashboard</h1>

      {/* Chart Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6 shadow-lg rounded-lg">
          <h2 className="text-xl font-semibold mb-4 text-center">Sales Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} fill="#8884d8" label>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6 shadow-lg rounded-lg">
          <h2 className="text-xl font-semibold mb-4 text-center">Stock Remaining</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="stock" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Table Section */}
      <div className="mt-8">
        <h2 className="text-2xl font-semibold mb-4 text-center">📦 Product Overview</h2>
        <div className="overflow-x-auto shadow-lg rounded-lg">
          <Table className="w-full bg-gray-50">
            <TableHeader>
              <TableRow className="bg-gray-300 text-white text-left">
                <TableCell>Item</TableCell>
                <TableCell>Price ($)</TableCell>
                <TableCell>Sales</TableCell>
                <TableCell>Revenue ($)</TableCell>
                <TableCell>Stock Remaining</TableCell>
                <TableCell>Recommendation</TableCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item, index) => (
                <TableRow key={index} className="hover:bg-gray-100 transition duration-200">
                  <TableCell>{item.item}</TableCell>
                  <TableCell>{item.price}</TableCell>
                  <TableCell>{item.sales}</TableCell>
                  <TableCell>{item.revenue}</TableCell>
                  <TableCell className="font-semibold">{item.stock_remaining}</TableCell>
                  <TableCell>
                    {item.stock_remaining > 100 ? (
                      <span className="text-green-600 font-medium">💰 Add More Discounts</span>
                    ) : item.stock_remaining < 40 ? (
                      <span className="text-red-600 font-medium">⚠️ Stock Up Due to High Demand</span>
                    ) : (
                      <span className="text-gray-600 font-medium">✔️ Stock is Balanced</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
