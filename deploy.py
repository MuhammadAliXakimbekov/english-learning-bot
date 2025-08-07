#!/usr/bin/env python3
"""
Education Bot Deployment Script
Helps deploy the bot to various platforms
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.OKGREEN):
    """Print colored message to terminal"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    """Print header message"""
    print_colored(f"\n🚀 {message}", Colors.HEADER + Colors.BOLD)

def print_success(message):
    """Print success message"""
    print_colored(f"✅ {message}", Colors.OKGREEN)

def print_warning(message):
    """Print warning message"""
    print_colored(f"⚠️  {message}", Colors.WARNING)

def print_error(message):
    """Print error message"""
    print_colored(f"❌ {message}", Colors.FAIL)

def run_command(command, capture_output=False):
    """Run a shell command"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, ""
    except Exception as e:
        print_error(f"Error running command '{command}': {e}")
        return False, ""

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print_header("Checking Prerequisites")
    
    prerequisites = {
        'python': 'python --version',
        'pip': 'pip --version',
        'git': 'git --version',
        'docker': 'docker --version'
    }
    
    missing = []
    for tool, command in prerequisites.items():
        success, output = run_command(command, capture_output=True)
        if success:
            print_success(f"{tool}: {output}")
        else:
            print_error(f"{tool}: Not found")
            missing.append(tool)
    
    return len(missing) == 0, missing

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Checking Environment Variables")
    
    env_file = Path('.env')
    if not env_file.exists():
        print_warning(".env file not found. Creating from template...")
        template_file = Path('env.template')
        if template_file.exists():
            template_file.rename('.env')
            print_success("Created .env from template. Please edit it with your actual values.")
            return False
        else:
            print_error("No .env or env.template file found!")
            return False
    
    # Check if .env has actual values (not template values)
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_telegram_bot_token_here' in content or 'your_gemini_api_key_here' in content:
            print_warning(".env file contains template values. Please update with actual values.")
            return False
    
    print_success("Environment variables file found and configured")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    success, _ = run_command('pip install -r requirements.txt')
    if success:
        print_success("Dependencies installed successfully")
        return True
    else:
        print_error("Failed to install dependencies")
        return False

def test_bot_locally():
    """Test the bot locally"""
    print_header("Testing Bot Locally")
    print("Starting bot for 10 seconds to test...")
    
    # Start bot in background and test health endpoint
    import threading
    import time
    import requests
    
    def start_bot():
        run_command('python main.py')
    
    # Start bot in background
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Wait for bot to start
    time.sleep(5)
    
    try:
        response = requests.get('http://localhost:10000/health', timeout=5)
        if response.status_code == 200:
            print_success("Bot health check passed!")
            return True
    except:
        pass
    
    print_error("Bot health check failed")
    return False

def deploy_docker():
    """Deploy using Docker"""
    print_header("Deploying with Docker")
    
    # Build Docker image
    print("Building Docker image...")
    success, _ = run_command('docker build -t education-bot .')
    if not success:
        print_error("Failed to build Docker image")
        return False
    
    print_success("Docker image built successfully")
    
    # Run with docker-compose
    print("Starting with docker-compose...")
    success, _ = run_command('docker-compose up -d')
    if not success:
        print_error("Failed to start with docker-compose")
        return False
    
    print_success("Bot deployed with Docker!")
    print("Check status with: docker-compose logs -f education-bot")
    return True

def deploy_render():
    """Deploy to Render.com"""
    print_header("Deploying to Render.com")
    
    print("To deploy to Render.com:")
    print("1. Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Ready for deployment'")
    print("   git push origin main")
    print()
    print("2. Go to https://render.com and create a new Web Service")
    print("3. Connect your GitHub repository")
    print("4. Use these settings:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python main.py")
    print("   - Add environment variables from your .env file")
    print()
    print("See DEPLOYMENT_GUIDE.md for detailed instructions.")

def deploy_heroku():
    """Deploy to Heroku"""
    print_header("Deploying to Heroku")
    
    # Check if Heroku CLI is installed
    success, _ = run_command('heroku --version', capture_output=True)
    if not success:
        print_error("Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    
    print("Deploying to Heroku...")
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    if app_name:
        success, _ = run_command(f'heroku create {app_name}')
    else:
        success, _ = run_command('heroku create')
    
    if not success:
        print_error("Failed to create Heroku app")
        return False
    
    # Set environment variables
    print("Setting environment variables...")
    with open('.env', 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                run_command(f'heroku config:set {key}={value}')
    
    # Deploy
    print("Deploying to Heroku...")
    success, _ = run_command('git push heroku main')
    if success:
        print_success("Deployed to Heroku successfully!")
        run_command('heroku open')
    else:
        print_error("Failed to deploy to Heroku")
    
    return success

def main():
    """Main deployment function"""
    print_colored("🤖 Education Bot Deployment Tool", Colors.HEADER + Colors.BOLD)
    print_colored("=" * 50, Colors.HEADER)
    
    # Check prerequisites
    prereq_ok, missing = check_prerequisites()
    if not prereq_ok:
        print_error(f"Missing prerequisites: {', '.join(missing)}")
        return
    
    # Check environment variables
    if not check_environment_variables():
        print_error("Please configure your .env file before deploying")
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Show deployment options
    print_header("Deployment Options")
    print("1. 🐳 Docker (Local)")
    print("2. ☁️  Render.com (Free Cloud)")
    print("3. 🟣 Heroku (Cloud)")
    print("4. 🧪 Test Locally Only")
    print("5. ❌ Exit")
    
    choice = input("\nSelect deployment option (1-5): ").strip()
    
    if choice == '1':
        deploy_docker()
    elif choice == '2':
        deploy_render()
    elif choice == '3':
        deploy_heroku()
    elif choice == '4':
        test_bot_locally()
    elif choice == '5':
        print("Goodbye! 👋")
        return
    else:
        print_error("Invalid choice")
        return
    
    print_header("Deployment Complete!")
    print("Your Education Bot should now be running! 🎉")

if __name__ == '__main__':
    main()
