import React from "react";

const AboutUs = () => {
  return (
    <div className="bg-white min-h-screen font-[Poppins] text-black py-12 px-6">
      <div className="max-w-6xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold">🛍 Welcome to ShopMart</h1>
        <p className="text-gray-400 mt-4 text-lg md:text-xl">
          Your ultimate AI-powered e-commerce marketplace, revolutionizing online shopping.
        </p>
      </div>

      {/* Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
        {features.map((feature, index) => (
          <div
            key={index}
            className="bg-black p-6 rounded-xl shadow-lg flex flex-col items-center text-center"
          >
            <div className="text-4xl text-gray-400 mb-3">{feature.icon}</div>
            <h3 className="text-xl font-semibold text-white">{feature.title}</h3>
            <p className="text-gray-400 mt-2">{feature.description}</p>
          </div>
        ))}
      </div>

      {/* Additional Info */}
      <div className="bg-white border border-black p-8 rounded-xl shadow-lg max-w-4xl mx-auto mt-12 text-center">
        <h2 className="text-2xl font-semibold text-black">Why Choose ShopMart?</h2>
        <p className="text-gray-400 mt-4 text-lg">
          ShopMart is not just an online store; it’s an intelligent marketplace that understands you.
          Our AI-driven recommendation system ensures personalized shopping experiences,
          increasing user engagement and business growth.
        </p>
      </div>
    </div>
  );
};

const features = [
  {
    title: "AI-Powered Recommendations",
    description:
      "Our hybrid AI model delivers personalized product suggestions based on user interactions.",
    icon: "🤖",
  },
  {
    title: "Loyalty Program",
    description:
      "Earn points on every purchase and redeem them for exciting rewards.",
    icon: "🎁",
  },
  {
    title: "Multi-Role Dashboards",
    description:
      "Dedicated dashboards for customers, businesses, and admins for seamless management.",
    icon: "📊",
  },
  {
    title: "Real-Time Analytics",
    description:
      "Track sales, conversions, and customer trends with live reporting dashboards.",
    icon: "📈",
  },
  {
    title: "Visual Search & NLP",
    description:
      "Upload images or use natural language to search and find products effortlessly.",
    icon: "🔍",
  },
  {
    title: "AI Chatbot Support",
    description:
      "24/7 AI-driven customer support to enhance shopping experiences.",
    icon: "💬",
  },
];

export default AboutUs;
