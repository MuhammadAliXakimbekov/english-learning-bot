@echo off
echo 🤖 Education Bot Deployment Tool (Windows)
echo ===============================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found
    if exist env.template (
        copy env.template .env
        echo ✅ Created .env from template
        echo 📝 Please edit .env file with your actual API keys before continuing
        notepad .env
        echo Press any key when you've finished editing .env...
        pause
    ) else (
        echo ❌ No .env or env.template file found!
        pause
        exit /b 1
    )
)

echo ✅ Environment file found

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed

REM Show deployment options
echo.
echo 🚀 Deployment Options:
echo 1. 🐳 Docker (if Docker is installed)
echo 2. ☁️  Render.com (Manual - opens guide)
echo 3. 🧪 Test Locally
echo 4. ❌ Exit
echo.

set /p choice="Select option (1-4): "

if "%choice%"=="1" (
    echo 🐳 Checking Docker...
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker not found! Please install Docker Desktop first.
        echo Opening Docker website...
        start https://www.docker.com/products/docker-desktop
        pause
        exit /b 1
    )
    
    echo ✅ Docker found
    echo 🔨 Building Docker image...
    docker build -t education-bot .
    if errorlevel 1 (
        echo ❌ Failed to build Docker image
        pause
        exit /b 1
    )
    
    echo 🚀 Starting with docker-compose...
    docker-compose up -d
    if errorlevel 1 (
        echo ❌ Failed to start with docker-compose
        pause
        exit /b 1
    )
    
    echo ✅ Bot deployed with Docker!
    echo 📊 Check logs with: docker-compose logs -f education-bot
    echo 🌐 Health check: http://localhost:10000/health
    
) else if "%choice%"=="2" (
    echo 🌐 Opening Render.com deployment guide...
    start DEPLOYMENT_GUIDE.md
    echo 📝 Follow the instructions in the guide to deploy to Render.com
    
) else if "%choice%"=="3" (
    echo 🧪 Testing bot locally...
    echo 🚀 Starting Education Bot...
    echo ⚠️  Press Ctrl+C to stop the bot
    python main.py
    
) else if "%choice%"=="4" (
    echo 👋 Goodbye!
    
) else (
    echo ❌ Invalid choice
    pause
    exit /b 1
)

echo.
echo 🎉 Process complete!
pause
