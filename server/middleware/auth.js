const jwt = require("jsonwebtoken");

const authenticate = (req, res, next) => {
  const token = req.header("Authorization");
  if (!token) return res.status(401).json({ error: "Access Denied" });

  try {
    const verified = jwt.verify(token, process.env.SECRET_KEY || "SECRET_KEY"); // ✅ Use environment variable
    req.user = verified;

    if (!req.user.role) {
      return res.status(403).json({ error: "User role is missing" });
    }

    next();
  } catch (err) {
    res.status(400).json({ error: "Invalid Token" });
  }
};

const authorize = (roles) => (req, res, next) => {
  if (!req.user || !req.user.role) {
    return res.status(403).json({ error: "Access Denied - No Role Assigned" });
  }

  if (!roles.includes(req.user.role)) {
    console.log("Unauthorized Role:", req.user.role);
    return res.status(403).json({ error: "Access Denied" });
  }

  next();
};

module.exports = { authenticate, authorize };
