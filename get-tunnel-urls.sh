#!/bin/bash

# Script to retrieve and display all active ngrok tunnel URLs

echo "Fetching tunnel URLs..."
echo ""

# Check if ngrok API is accessible
if ! curl -s localhost:4040/api/tunnels > /dev/null 2>&1; then
    echo "Cannot connect to ngrok API"
    echo "Make sure ngrok tunnels are running"
    exit 1
fi

# Get all tunnels
TUNNELS=$(curl -s localhost:4040/api/tunnels)

# Parse and display URLs
echo "Active Tunnel URLs:"
echo "====================="
echo ""

# Frontend
FRONTEND_URL=$(echo $TUNNELS | jq -r '.tunnels[] | select(.name=="frontend") | .public_url')
if [ ! -z "$FRONTEND_URL" ] && [ "$FRONTEND_URL" != "null" ]; then
    echo "Frontend:    $FRONTEND_URL"
else
    echo "Frontend tunnel not found"
fi

# Product API
PRODUCT_URL=$(echo $TUNNELS | jq -r '.tunnels[] | select(.name=="product-api") | .public_url')
if [ ! -z "$PRODUCT_URL" ] && [ "$PRODUCT_URL" != "null" ]; then
    echo "Product API: $PRODUCT_URL"
else
    echo "Product API tunnel not found"
fi

# Order API
ORDER_URL=$(echo $TUNNELS | jq -r '.tunnels[] | select(.name=="order-api") | .public_url')
if [ ! -z "$ORDER_URL" ] && [ "$ORDER_URL" != "null" ]; then
    echo "Order API:   $ORDER_URL"
else
    echo "Order API tunnel not found"
fi

echo ""
echo "Web Interface: http://localhost:4040"
echo ""

# Save URLs to file
cat > tunnel-urls.txt << EOF
Frontend: $FRONTEND_URL
Product API: $PRODUCT_URL
Order API: $ORDER_URL
EOF

echo "URLs saved to tunnel-urls.txt"