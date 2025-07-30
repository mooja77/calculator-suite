#!/bin/bash
# Render build script to verify files and fix startup

echo "=== Checking deployment files ==="
echo "Current directory: $(pwd)"
echo "Files in root:"
ls -la

echo ""
echo "=== Checking for wsgi.py ==="
if [ -f "wsgi.py" ]; then
    echo "✅ wsgi.py exists"
    echo "Content:"
    head -20 wsgi.py
else
    echo "❌ wsgi.py NOT FOUND"
fi

echo ""
echo "=== Checking Procfile ==="
if [ -f "Procfile" ]; then
    echo "✅ Procfile exists"
    echo "Content:"
    cat Procfile
else
    echo "❌ Procfile NOT FOUND"
fi

echo ""
echo "=== Python path check ==="
echo "PYTHONPATH: $PYTHONPATH"
echo "Python version: $(python --version)"

echo ""
echo "=== Testing app import ==="
python -c "import sys; print('Python path:', sys.path)"
python -c "from wsgi import app; print('✅ wsgi import successful')" || echo "❌ wsgi import failed"
python -c "from app import create_app; print('✅ app package import successful')" || echo "❌ app package import failed"