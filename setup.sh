#!/bin/bash
# CodeInsight - Linux/Mac Setup Script

echo ""
echo "========================================"
echo "CodeInsight - Setup"
echo "========================================"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Install with: brew install python3 (Mac) or apt-get install python3 (Ubuntu)"
    exit 1
fi

echo "OK: Python3 is installed"
python3 --version
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "OK: Virtual environment created"
else
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo ""

# Install requirements
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

echo "OK: Dependencies installed"
echo ""

# Check MySQL
echo "Checking MySQL..."
if ! command -v mysql &> /dev/null; then
    echo "WARNING: MySQL is not installed"
    echo "Install with: brew install mysql (Mac) or apt-get install mysql-server (Ubuntu)"
    echo ""
else
    echo "OK: MySQL is installed"
    mysql --version
    echo ""
fi

# Display next steps
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Create database:"
echo "   mysql -u root -p < database.sql"
echo ""
echo "2. Update database credentials in app.py"
echo ""
echo "3. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "4. Run application:"
echo "   python app.py"
echo ""
echo "5. Open browser and go to:"
echo "   http://localhost:5000"
echo ""
echo "========================================"
echo ""
