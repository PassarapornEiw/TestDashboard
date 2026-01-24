#!/bin/bash

# Test Dashboard Deployment Script
PROJECT_NAME="Test Dashboard"
PROJECT_PATH="/opt/Test Dashboard"
VENV_PATH="$PROJECT_PATH/venv"
SERVICE_NAME="test-dashboard"
AUTOMATION_PROJECT_PATH="/opt/Automation Project"
RESULTS_PATH="$AUTOMATION_PROJECT_PATH/results"

echo "🚀 Starting deployment of $PROJECT_NAME..."

# Stop service if running
echo "⏹️ Stopping service..."
sudo systemctl stop $SERVICE_NAME

# Update code from git (if using git)
echo " Updating code..."
cd $PROJECT_PATH
git pull origin main

# Activate virtual environment
source $VENV_PATH/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers if needed
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Verify Automation Project path exists
if [ ! -d "$AUTOMATION_PROJECT_PATH" ]; then
    echo "❌ Error: Automation Project directory not found at $AUTOMATION_PROJECT_PATH"
    echo "   Please ensure the Automation Project is deployed first"
    exit 1
fi

# Verify results directory exists
if [ ! -d "$RESULTS_PATH" ]; then
    echo "❌ Error: results directory not found at $RESULTS_PATH"
    echo "   Please ensure the Automation Project has been run at least once"
    exit 1
fi

echo "✅ Automation Project and results directory verified"
echo "📊 Results directory contains:"
ls -la "$RESULTS_PATH" | head -10

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R jenkins:jenkins $PROJECT_PATH
chmod +x $PROJECT_PATH/Dashboard_Report/run_production.py

# Reload systemd and restart service
echo "🔄 Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Check status
echo "📊 Service status:"
sudo systemctl status $SERVICE_NAME

echo "✅ Deployment completed!"
echo "🌐 Dashboard should be available at: http://$(hostname -I | awk '{print $1}'):5000"
echo "📊 Reading results from: $RESULTS_PATH"
