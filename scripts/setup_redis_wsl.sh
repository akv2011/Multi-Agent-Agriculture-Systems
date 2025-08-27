#!/bin/bash

# Redis Setup Script for WSL
# Run this after WSL2 is installed and you're in Ubuntu

echo "🚀 Setting up Redis in WSL Ubuntu..."
echo

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Add Redis repository
echo "🔑 Adding Redis GPG key..."
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "📋 Adding Redis repository..."
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# Update package list with new repository
echo "🔄 Updating package list with Redis repository..."
sudo apt-get update

# Install Redis
echo "⬇️ Installing Redis..."
sudo apt-get install -y redis

# Start Redis service
echo "🚀 Starting Redis server..."
sudo service redis-server start

# Test Redis
echo "🧪 Testing Redis connection..."
redis-cli ping

if [ $? -eq 0 ]; then
    echo "✅ Redis is working!"
    echo "📡 Redis server is running on localhost:6379"
    echo
    echo "🎯 Your Multi-Agent Agriculture System can now use Redis!"
    echo
    echo "To start Redis in the future, run:"
    echo "sudo service redis-server start"
    echo
    echo "To check if Redis is running:"
    echo "redis-cli ping"
else
    echo "❌ Redis test failed"
fi

echo
echo "🌾 Ready for agriculture system!"
