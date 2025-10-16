from flask import Flask, jsonify, request
from flask_cors import CORS
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
ORDERS = [
    {"id": 1, "customer": "John Doe", "product_id": 1,
        "quantity": 2, "status": "completed"},
    {"id": 2, "customer": "Jane Smith", "product_id": 2,
        "quantity": 5, "status": "pending"},
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
    logger.info(f"Response: {response.status_code}")
    return response

# Health check endpoints


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "UP",
        "service": "order-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200


@app.route('/ready', methods=['GET'])
def ready():
    return jsonify({
        "ready": True,
        "service": "order-api"
    }), 200

# Order endpoints


@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    try:
        logger.info("Fetching all orders")
        return jsonify(ORDERS), 200
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order by ID"""
    try:
        order = next((o for o in ORDERS if o["id"] == order_id), None)
        if not order:
            logger.warning(f"Order {order_id} not found")
            return jsonify({"error": "Order not found"}), 404
        logger.info(f"Retrieved order {order_id}")
        return jsonify(order), 200
    except Exception as e:
        logger.error(f"Error fetching order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/orders', methods=['POST'])
def create_order():
    """Create new order"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ["customer", "product_id", "quantity"]):
            return jsonify({"error": "Missing required fields"}), 400

        new_order = {
            "id": max([o["id"] for o in ORDERS]) + 1 if ORDERS else 1,
            "customer": data["customer"],
            "product_id": data["product_id"],
            "quantity": data["quantity"],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        ORDERS.append(new_order)
        logger.info(f"Created order {new_order['id']}")
        return jsonify(new_order), 201
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update order"""
    try:
        order = next((o for o in ORDERS if o["id"] == order_id), None)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        data = request.get_json()
        order.update(data)
        logger.info(f"Updated order {order_id}")
        return jsonify(order), 200
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    """Cancel order"""
    try:
        order = next((o for o in ORDERS if o["id"] == order_id), None)
        if not order:
            return jsonify({"error": "Order not found"}), 404

        order["status"] = "cancelled"
        logger.info(f"Cancelled order {order_id}")
        return jsonify(order), 200
    except Exception as e:
        logger.error(f"Error cancelling order: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Metrics endpoint


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return jsonify({"orders_count": len(ORDERS)}), 200

# Error handlers


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
