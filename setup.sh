#!/bin/bash

echo "========================================="
echo "EpicDeals AI Price Research Tool"
echo "Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your actual configuration:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - SMTP credentials"
    echo "   - Other settings"
    echo ""
else
    echo ""
    echo "✓ .env file already exists"
fi

# Check for ChromeDriver (for Selenium)
echo ""
echo "Checking for ChromeDriver..."
if ! command -v chromedriver &> /dev/null; then
    echo "⚠️  ChromeDriver not found. Facebook Marketplace scraping will not work."
    echo "   Install with: brew install chromedriver (macOS)"
    echo "   Or: sudo apt-get install chromium-chromedriver (Linux)"
else
    echo "✓ ChromeDriver found"
fi

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python app.py"
echo ""
echo "The application will be available at http://localhost:5000"
echo ""
