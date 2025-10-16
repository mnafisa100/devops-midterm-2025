from flask import Flask, jsonify, request
from flask_cors import CORS
from functools import wraps
import logging
import os
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock database
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 1299.99, "stock": 50},
    {"id": 2, "name": "Mouse", "price": 29.99, "stock": 200},
    {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 150},
    {"id": 4, "name": "Monitor", "price": 399.99, "stock": 30},
    {"id": 5, "name": "Headphones", "price": 199.99, "stock": 75},
]

# Middleware for logging


@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path}", extra={
        "timestamp": datetime.utcnow().isoformat(),
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr
    })


@app.after_request
def log_response(response):
    logger.info(f"Response: {response.status_code}", extra={
        "status_code": response.status_code,
        "content_length": response.content_length
    })
    return response

# Health check endpoints


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "UP",
        "service": "product-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200


@app.route('/ready', methods=['GET'])
def ready():
    return jsonify({
        "ready": True,
        "service": "product-api"
    }), 200

# Product endpoints


@app.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        logger.info("Fetching all products")
        return jsonify(PRODUCTS), 200
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    try:
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if not product:
            logger.warning(f"Product {product_id} not found")
            return jsonify({"error": "Product not found"}), 404
        logger.info(f"Retrieved product {product_id}")
        return jsonify(product), 200
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/products', methods=['POST'])
def create_product():
    """Create new product"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ["name", "price", "stock"]):
            return jsonify({"error": "Missing required fields"}), 400

        new_product = {
            "id": max([p["id"] for p in PRODUCTS]) + 1,
            "name": data["name"],
            "price": data["price"],
            "stock": data["stock"]
        }
        PRODUCTS.append(new_product)
        logger.info(f"Created product {new_product['id']}")
        return jsonify(new_product), 201
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update product"""
    try:
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        data = request.get_json()
        product.update(data)
        logger.info(f"Updated product {product_id}")
        return jsonify(product), 200
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete product"""
    try:
        global PRODUCTS
        if not any(p["id"] == product_id for p in PRODUCTS):
            return jsonify({"error": "Product not found"}), 404
        PRODUCTS = [p for p in PRODUCTS if p["id"] != product_id]
        logger.info(f"Deleted product {product_id}")
        return jsonify({"message": "Product deleted"}), 204
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Metrics endpoint for Prometheus


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return jsonify({"products_count": len(PRODUCTS)}), 200

# Error handlers


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
