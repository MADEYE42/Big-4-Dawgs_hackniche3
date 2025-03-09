import express from "express";
import dotenv from "dotenv";
import pkg from "pg";
const { Pool } = pkg;
import { Client } from '@elastic/elasticsearch';

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

const pool = new Pool({
    user: process.env.DB_USER,
    host: process.env.DB_HOST,
    database: process.env.DB_NAME,
    password: process.env.DB_PASSWORD,
    port: process.env.DB_PORT,
});

const client = new Client({
    node: 'http://localhost:9200',
});

let globalUserId = "Guest"; // Default user ID



app.use(express.json());
app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', 'http://localhost:3001'); // Allow your frontend origin
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS'); // Allowed methods
    res.header('Access-Control-Allow-Headers', 'Content-Type'); // Allowed headers
    next();
});

pool.connect()
    .then(() => console.log("Connected to PostgreSQL"))
    .catch((err) => console.error("Database connection error", err));

app.get("/home", async (req, res) => {
    try {
        const result = await pool.query("SELECT DISTINCT ON (category) category, image_url FROM amazon_products;");

        res.json(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send("Server Error");
    }
});

app.post("/view-product", async (req, res) => {
    const { asin } = req.body;
    if (!asin) {
        return res.status(400).json({ error: "Product ID is required" });
    }

    try {
        const query = "SELECT * FROM public.amazon_products WHERE asin = $1 LIMIT 1";
        const result = await pool.query(query, [asin]);

        if (result.rows.length === 0) {
            return res.status(404).json({ error: "Product not found" });
        }

        try {
            await client.index({
                index: "product-views",
                body: {
                    timestamp: new Date().toISOString(),
                    userId: globalUserId, // Use global user ID
                    asin: result.rows[0].asin,
                    productTitle: result.rows[0].title,
                    category: result.rows[0].category,
                    price: result.rows[0].price
                },
            });
            console.log(`Logged product view for ASIN: ${asin}, UserID: ${globalUserId} in Elasticsearch`);
        } catch (esError) {
            console.error("Error logging to Elasticsearch:", esError);
        }

        res.json(result.rows[0]);
    } catch (error) {
        console.error("Error fetching product:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
});



app.get("/init_suggestion", async (req, res) => {
    try {
        const result = await pool.query("SELECT asin, image_url, title, category, price FROM public.amazon_products ORDER BY RANDOM() LIMIT 9;");

        res.json(result.rows);
        console.log(result.rows);
    } catch (err) {
        console.error(err);
        res.status(500).send("Server Error");
    }
});

app.post("/login", async (req, res) => {
    try {
        const { email, role } = req.body;
        if (!email) {
            return res.status(400).json({ message: "Email is required" });
        }

        const existingUser = await pool.query("SELECT id, role, counter FROM users WHERE email = $1", [email]);

        let loginStatus, statusCode, userRole, userCounter;

        if (existingUser.rows.length > 0) {
            globalUserId = existingUser.rows[0].id; // Update global user ID
            userRole = existingUser.rows[0].role;
            userCounter = existingUser.rows[0].counter;
            await pool.query("UPDATE users SET counter = counter + 1 WHERE email = $1", [email]);
            loginStatus = "Login successful";
            statusCode = 200;
        } else {
            const newUserRole = role || 'customer';
            const result = await pool.query(
                "INSERT INTO users (email, role) VALUES ($1, $2) RETURNING id, role, counter",
                [email, newUserRole]
            );
            globalUserId = result.rows[0].id;
            userRole = result.rows[0].role;
            userCounter = result.rows[0].counter;
            loginStatus = "User registered successfully";
            statusCode = 201;
        }

        try {
            await client.index({
                index: "login-logs",
                body: {
                    timestamp: new Date(),
                    message: loginStatus,
                    email: email,
                    userId: globalUserId,
                    status: statusCode,
                    role: userRole,
                    counter: userCounter,
                    formData: req.body,
                },
            });
            console.log("Logged login to Elasticsearch");
        } catch (esError) {
            console.error("Error logging login to Elasticsearch:", esError);
        }

        return res.status(statusCode).json({ message: loginStatus, userId: globalUserId, role: userRole, counter: userCounter });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Internal Server Error" });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
