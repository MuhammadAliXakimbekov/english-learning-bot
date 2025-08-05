#!/usr/bin/env python3
"""
Start script for Education Bot
Alternative entry point for deployment platforms
"""

import os
import sys

def main():
    """Main entry point"""
    # Ensure we're in the right directory
    if __name__ == '__main__':
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the main bot
    from main import main as bot_main
    bot_main()

if __name__ == '__main__':
    main()