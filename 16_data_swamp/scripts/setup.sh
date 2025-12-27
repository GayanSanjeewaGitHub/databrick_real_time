#!/usr/bin/env bash
# Setup script for the data pipeline

echo "====================================="
echo "Data Pipeline Setup"
echo "====================================="

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ Created .env file (please review and update if needed)"
fi

# Create Python virtual environment
echo ""
echo "Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
if [ -f venv/Scripts/activate ]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

echo "✓ Virtual environment created"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✓ Dependencies installed"

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/raw/transactions
mkdir -p data/raw/weblogs
mkdir -p data/processed
mkdir -p data/swamp

echo "✓ Directories created"

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Review and update .env file if needed"
echo "2. Start services: docker-compose up -d"
echo "3. Wait for services to be ready (~2 minutes)"
echo "4. Run: python src/data_generator.py"
echo "5. Run: python src/pipeline_no_hms.py  (Data Swamp demo)"
echo "6. Run: python src/pipeline_with_hms.py (Governed approach)"
echo "7. Run: python src/propensity_model.py (Full pipeline)"
echo ""
