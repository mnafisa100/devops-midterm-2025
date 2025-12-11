#!/bin/bash

# Stop all tunnels and port forwarding

echo "Stopping all tunnels and port forwarding..."

# Kill all ngrok processes
echo "Stopping ngrok tunnels..."
pkill ngrok

# Kill all kubectl port-forward processes
echo "Stopping port forwarding..."
pkill -f "kubectl port-forward"

# Clean up log files
rm -f frontend-tunnel.log product-tunnel.log order-tunnel.log tunnel-pids.txt

echo "All tunnels stopped"
echo "Log files cleaned up"