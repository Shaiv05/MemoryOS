#!/usr/bin/env bash
set -e

echo "Installing tool versions..."
mise install

echo "Setting up backend..."
cd backend

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "Setting up frontend..."
cd ../frontend

npm install

echo ""
echo "✅ MemoryOS setup completed successfully!"
echo ""
echo "To start development:"
echo "Backend:"
echo "  cd backend"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Frontend:"
echo "  cd frontend"
echo "  npm run dev"
