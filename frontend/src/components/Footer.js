const Footer = () => {
    return (
      <footer className="bg-black text-white py-8 px-4 font-[Poppins]">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center text-center md:text-left">
          {/* Company Info */}
          <div className="mb-4 md:mb-0">
            <h2 className="text-lg font-semibold">ShopMart</h2>
            <p className="text-sm">Your one-stop marketplace for all your needs.</p>
          </div>
          
          {/* Quick Links */}
          <div className="flex flex-col md:flex-row gap-4 text-sm">
            <a href="/about" className="hover:underline">About</a>
            <a href="/contact" className="hover:underline">Contact</a>
            <a href="/privacy" className="hover:underline">Privacy Policy</a>
          </div>
          
          {/* Social Media */}
          <div className="flex gap-4 text-xl">
            <a href="#" className="hover:text-gray-400">🔵</a>
            <a href="#" className="hover:text-gray-400">🐦</a>
            <a href="#" className="hover:text-gray-400">📸</a>
          </div>
        </div>
        
        {/* Copyright */}
        <div className="text-center text-sm mt-4">© 2025 ShopMart. All rights reserved.</div>
      </footer>
    );
  };
  
  export default Footer;