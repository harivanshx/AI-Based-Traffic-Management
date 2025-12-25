
echo "AI-Based Traffic Management System - Setup"


echo "[1/4] Checking Python installation..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi
echo ""

echo "[2/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi
echo "Virtual environment created successfully!"
echo ""

echo "[3/4] Activating virtual environment..."
source venv/bin/activate
echo ""

echo "[4/4] Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

echo "Setup Complete!"

echo "To run the system:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run with webcam: python main.py"
echo "  3. Run with video: python main.py --input your_video.mp4"
echo ""
echo "For more information, see README.md"
