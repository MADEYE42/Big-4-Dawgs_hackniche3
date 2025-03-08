import React, { useState } from "react";
import { FiMail, FiPhone, FiMapPin } from "react-icons/fi";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const ContactUs = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
    access_key: "a8661bf2-26cf-46b5-818d-ab5baadedb24", // Web3Forms API Key
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch("https://api.web3forms.com/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      toast.success("✅ Message sent successfully!");
      setFormData({ name: "", email: "", message: "", access_key: formData.access_key });
    } else {
      toast.error("❌ Something went wrong! Please try again.");
    }
  };

  return (
    <div className="bg-white min-h-screen font-[Poppins] text-black py-12 px-6">
      <ToastContainer position="top-right" autoClose={3000} />
      <div className="max-w-5xl mx-auto text-center">
        <h1 className="text-4xl md:text-5xl font-extrabold">📬 Get in Touch</h1>
        <p className="text-gray-400 mt-4 text-lg md:text-xl">
          We'd love to hear from you! Feel free to reach out with any inquiries.
        </p>
      </div>

      {/* Contact Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center mt-12">
        <div className="bg-black p-6 rounded-xl shadow-lg flex flex-col items-center">
          <FiMail className="text-4xl text-gray-400 mb-3" />
          <h3 className="text-xl font-semibold text-white">Email Us</h3>
          <p className="text-gray-400">support@shopmart.com</p>
        </div>
        <div className="bg-black p-6 rounded-xl shadow-lg flex flex-col items-center">
          <FiPhone className="text-4xl text-gray-400 mb-3" />
          <h3 className="text-xl font-semibold text-white">Call Us</h3>
          <p className="text-gray-400">+1 (234) 567-890</p>
        </div>
        <div className="bg-black p-6 rounded-xl shadow-lg flex flex-col items-center">
          <FiMapPin className="text-4xl text-gray-400 mb-3" />
          <h3 className="text-xl font-semibold text-white">Visit Us</h3>
          <p className="text-gray-400">123 Market Street, NY</p>
        </div>
      </div>

      {/* Contact Form */}
      <div className="bg-white border border-black p-8 rounded-xl shadow-lg max-w-3xl mx-auto mt-12">
        <h2 className="text-2xl font-semibold text-center mb-6 text-black">💬 Send us a Message</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="hidden" name="access_key" value={formData.access_key} />
          <div>
            <label className="block text-gray-400 font-medium">Your Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full p-3 border rounded-md bg-white text-black focus:ring-2 focus:ring-black"
              placeholder="Gouresh Madye"
            />
          </div>
          <div>
            <label className="block text-gray-400 font-medium">Your Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full p-3 border rounded-md bg-white text-black focus:ring-2 focus:ring-black"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className="block text-gray-400 font-medium">Your Message</label>
            <textarea
              name="message"
              value={formData.message}
              onChange={handleChange}
              required
              rows="4"
              className="w-full p-3 border rounded-md bg-white text-black focus:ring-2 focus:ring-black"
              placeholder="Write your message here..."
            ></textarea>
          </div>
          <button
            type="submit"
            className="w-full bg-black text-white py-3 rounded-md text-lg font-semibold shadow-md hover:bg-gray-400 transition"
          >
            ✉️ Send Message
          </button>
        </form>
      </div>
    </div>
  );
};

export default ContactUs;
