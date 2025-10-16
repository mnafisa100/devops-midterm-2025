const express = require('express');
const axios = require('axios');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Environment variables with defaults
const PRODUCT_API_URL = process.env.PRODUCT_API_URL || 'http://product-api:5000';
const ORDER_API_URL = process.env.ORDER_API_URL || 'http://order-api:8000';
const NODE_ENV = process.env.NODE_ENV || 'development';
const LOG_LEVEL = process.env.LOG_LEVEL || 'info';

// Logging utility
const log = (level, message, data = {}) => {
    const timestamp = new Date().toISOString();
    console.log(JSON.stringify({
        timestamp,
        level,
        service: 'frontend',
        message,
        ...data,
        environment: NODE_ENV
    }));
};

// Health check endpoint
app.get('/health', (req, res) => {
    const health = {
        status: 'UP',
        service: 'frontend',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        environment: NODE_ENV,
        memory: process.memoryUsage()
    };
    log('info', 'Health check performed', { status: 'UP' });
    res.status(200).json(health);
});

// Ready probe endpoint
app.get('/ready', (req, res) => {
    res.status(200).json({ 
        ready: true,
        service: 'frontend',
        timestamp: new Date().toISOString()
    });
});

// Serve static index.html for root path
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// API Routes - Product Service
app.get('/api/products', async (req, res) => {
    try {
        log('info', 'Fetching products from Product API');
        const response = await axios.get(`${PRODUCT_API_URL}/products`, {
            timeout: 5000
        });
        log('info', 'Products fetched successfully', { count: response.data.length });
        res.json(response.data);
    } catch (error) {
        log('error', 'Failed to fetch products', {
            error: error.message,
            url: PRODUCT_API_URL
        });
        res.status(503).json({
            error: 'Product service unavailable',
            message: error.message
        });
    }
});

app.get('/api/products/:id', async (req, res) => {
    try {
        const { id } = req.params;
        log('info', 'Fetching product details', { productId: id });
        const response = await axios.get(`${PRODUCT_API_URL}/products/${id}`, {
            timeout: 5000
        });
        log('info', 'Product details fetched', { productId: id });
        res.json(response.data);
    } catch (error) {
        log('error', 'Failed to fetch product', {
            error: error.message,
            productId: req.params.id
        });
        res.status(503).json({
            error: 'Product service unavailable',
            message: error.message
        });
    }
});

app.post('/api/products', async (req, res) => {
    try {
        log('info', 'Creating new product', { body: req.body });
        const response = await axios.post(`${PRODUCT_API_URL}/products`, req.body, {
            timeout: 5000
        });
        log('info', 'Product created successfully', { productId: response.data.id });
        res.status(201).json(response.data);
    } catch (error) {
        log('error', 'Failed to create product', {
            error: error.message
        });
        res.status(503).json({
            error: 'Product service unavailable',
            message: error.message
        });
    }
});

// API Routes - Order Service
app.get('/api/orders', async (req, res) => {
    try {
        log('info', 'Fetching orders from Order API');
        const response = await axios.get(`${ORDER_API_URL}/orders`, {
            timeout: 5000
        });
        log('info', 'Orders fetched successfully', { count: response.data.length });
        res.json(response.data);
    } catch (error) {
        log('error', 'Failed to fetch orders', {
            error: error.message,
            url: ORDER_API_URL
        });
        res.status(503).json({
            error: 'Order service unavailable',
            message: error.message
        });
    }
});

app.get('/api/orders/:id', async (req, res) => {
    try {
        const { id } = req.params;
        log('info', 'Fetching order details', { orderId: id });
        const response = await axios.get(`${ORDER_API_URL}/orders/${id}`, {
            timeout: 5000
        });
        log('info', 'Order details fetched', { orderId: id });
        res.json(response.data);
    } catch (error) {
        log('error', 'Failed to fetch order', {
            error: error.message,
            orderId: req.params.id
        });
        res.status(503).json({
            error: 'Order service unavailable',
            message: error.message
        });
    }
});

app.post('/api/orders', async (req, res) => {
    try {
        log('info', 'Creating new order', { body: req.body });
        const response = await axios.post(`${ORDER_API_URL}/orders`, req.body, {
            timeout: 5000
        });
        log('info', 'Order created successfully', { orderId: response.data.id });
        res.status(201).json(response.data);
    } catch (error) {
        log('error', 'Failed to create order', {
            error: error.message
        });
        res.status(503).json({
            error: 'Order service unavailable',
            message: error.message
        });
    }
});

// Health check endpoints for the dashboard
app.get('/api/health/products', async (req, res) => {
    try {
        const response = await axios.get(`${PRODUCT_API_URL}/health`, {
            timeout: 3000
        });
        res.json({ 
            status: 'healthy',
            service: 'product-api',
            details: response.data
        });
    } catch (error) {
        res.status(503).json({ 
            status: 'unhealthy',
            service: 'product-api',
            error: error.message
        });
    }
});

app.get('/api/health/orders', async (req, res) => {
    try {
        const response = await axios.get(`${ORDER_API_URL}/health`, {
            timeout: 3000
        });
        res.json({ 
            status: 'healthy',
            service: 'order-api',
            details: response.data
        });
    } catch (error) {
        res.status(503).json({ 
            status: 'unhealthy',
            service: 'order-api',
            error: error.message
        });
    }
});

// 404 handler
app.use((req, res) => {
    log('warn', 'Route not found', { path: req.path, method: req.method });
    res.status(404).json({
        error: 'Not Found',
        path: req.path,
        message: 'The requested resource was not found'
    });
});

// Error handler
app.use((err, req, res, next) => {
    log('error', 'Unhandled error', {
        error: err.message,
        stack: err.stack
    });
    res.status(500).json({
        error: 'Internal Server Error',
        message: NODE_ENV === 'development' ? err.message : 'An error occurred'
    });
});

// Graceful shutdown
const gracefulShutdown = () => {
    log('info', 'Graceful shutdown initiated');
    server.close(() => {
        log('info', 'HTTP server closed');
        process.exit(0);
    });
    
    setTimeout(() => {
        log('error', 'Forced shutdown after timeout');
        process.exit(1);
    }, 10000);
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Start server
const server = app.listen(PORT, () => {
    log('info', `Frontend server started on port ${PORT}`, {
        port: PORT,
        productApiUrl: PRODUCT_API_URL,
        orderApiUrl: ORDER_API_URL,
        environment: NODE_ENV
    });
});