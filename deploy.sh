#!/bin/bash

# Stock Screener Dashboard Deployment Script

echo "🚀 Stock Screener Dashboard Deployment Helper"
echo "=============================================="

echo ""
echo "📋 Available deployment options:"
echo "1. Streamlit Community Cloud (FREE - Recommended)"
echo "2. Railway (FREE tier available)"  
echo "3. Render (FREE tier available)"
echo "4. Docker (Local/Self-hosted)"
echo "5. Heroku (Paid)"

echo ""
echo "📦 Prerequisites check:"

# Check if git is available
if command -v git &> /dev/null; then
    echo "✅ Git is installed"
else
    echo "❌ Git is not installed - required for cloud deployment"
fi

# Check if docker is available  
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"
else
    echo "⚠️  Docker not found (optional - needed for containerized deployment)"
fi

echo ""
echo "🔧 Next steps:"
echo ""
echo "For Streamlit Cloud (Easiest):"
echo "1. Push this code to a GitHub repository"
echo "2. Visit https://share.streamlit.io"
echo "3. Connect your GitHub account"
echo "4. Select this repository" 
echo "5. Set main file as: dashboard.py"
echo "6. Deploy! 🎉"

echo ""
echo "For Railway:"
echo "1. Visit https://railway.app"
echo "2. Connect GitHub repository"
echo "3. Deploy automatically (uses Procfile)"

echo ""
echo "For Render:"
echo "1. Visit https://render.com" 
echo "2. Create new Web Service"
echo "3. Connect GitHub repository"
echo "4. Uses render.yaml automatically"

echo ""
echo "For Docker (local):"
echo "docker build -t stock-screener ."
echo "docker run -p 8501:8501 stock-screener"

echo ""
echo "📝 Don't forget to:"
echo "- Update README.md with your live URL"
echo "- Test the deployment thoroughly"
echo "- Monitor usage and performance"

echo ""
echo "🎯 Your dashboard will be accessible from anywhere once deployed!"