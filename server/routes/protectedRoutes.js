const express = require("express");
const { authenticate, authorize } = require("../middleware/auth");
const router = express.Router();

router.get("/customer", authenticate, authorize(["customer"]), (req, res) => {
  res.json({ message: "Customer Dashboard" });
});

router.get("/seller", authenticate, authorize(["seller"]), (req, res) => {
  res.json({ message: "Seller Dashboard" });
});

router.get("/admin", authenticate, authorize(["admin"]), (req, res) => {
  res.json({ message: "Admin Dashboard" });
});

module.exports = router;
