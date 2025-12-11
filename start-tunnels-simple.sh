#!/bin/bash

#  tunnel setup using ngrok config file

echo "Starting TechCommerce tunnels..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "ngrok is not installed"
    echo "Install: brew install ngrok/ngrok/ngrok (Mac) or visit https://ngrok.com/download"
    exit 1
fi

# Check if ngrok.yml exists
if [ ! -f ngrok.yml ]; then
    echo "ngrok.yml not found"
    echo "Please create ngrok.yml with your auth token"
    exit 1
fi

# Start port forwarding in background
echo "Starting port forwarding..."
echo "You may need to run these in separate terminals if this fails:"
echo "  Terminal 1: kubectl port-forward svc/frontend 3000:3000 -n techcommerce"
echo "  Terminal 2: kubectl port-forward svc/product-api 5000:5000 -n techcommerce"
echo "  Terminal 3: kubectl port-forward svc/order-api 8000:8000 -n techcommerce"
echo ""

kubectl port-forward svc/frontend 3000:3000 -n techcommerce &
kubectl port-forward svc/product-api 5000:5000 -n techcommerce &
kubectl port-forward svc/order-api 8000:8000 -n techcommerce &

sleep 3

# Start all tunnels using ngrok config
echo "Starting ngrok tunnels..."
ngrok start --all --config=ngrok.yml

# When ngrok exits, clean up port forwarding
echo "Stopping port forwarding..."
pkill -f "kubectl port-forward"