#!/bin/bash

# Create and activate conda environment
echo "Creating conda environment 'agentweaver'..."
conda create -n agentweaver python=3.11 -y

# Activate environment
echo "Activating conda environment..."
conda activate agentweaver

# Install backend dependencies
echo "Installing backend dependencies..."
cd /home/hari/Music/Multi-Agent-Agriculture-Systems/AgentWeaver
pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Setup complete! To start the system:"
echo "1. Activate conda environment: conda activate agentweaver"
echo "2. Start backend: python main.py"
echo "3. In new terminal, start frontend: cd frontend && npm run dev"
