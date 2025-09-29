#!/usr/bin/env python3
"""
Veritas Launcher - One-click startup for the complete system
Checks dependencies, starts API server, and opens frontend.

Usage: python start_veritas.py
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def print_banner():
    print("=" * 70)
    print("🚀 Veritas AI Research Platform".center(70))
    print("Starting complete system with frontend integration...".center(70))
    print("=" * 70)
    print()


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8+ required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again")
        return False

    print(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True


def check_environment():
    """Check if .env file exists with API keys."""
    env_path = Path(".env")
    if not env_path.exists():
        print("WARNING: .env file not found")
        print("   Creating template .env file...")

        template_content = """# Veritas AI Research Platform - API Keys
# Please fill in your API keys below

# OpenAI API Key (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Tavily Search API Key (Optional but recommended)
TAVILY_API_KEY=your_tavily_api_key_here

# Google API Key (Optional, for Gemini models)
GOOGLE_API_KEY=your_google_api_key_here
"""
        with open(env_path, "w") as f:
            f.write(template_content)

        print("   Template created. Please edit .env file with your API keys")
        print("   Run: python setup_api_keys.py for guided setup")
        return False

    # Check if keys are configured
    with open(env_path, "r") as f:
        content = f.read()

    if "your_openai_api_key_here" in content:
        print("WARNING: OpenAI API key not configured")
        print("   Run: python setup_api_keys.py to configure")
        return False

    print("Environment configuration found")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "crewai",
        "langchain_openai",
        "pandas",
        "matplotlib",
        "requests",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print()
        print("Install with: pip install -r requirements.txt")
        return False

    print("All required dependencies installed")
    return True


def start_api_server():
    """Start the FastAPI server in background."""
    print("Starting API server...")

    try:
        # Start server as subprocess
        process = subprocess.Popen(
            [sys.executable, "api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a moment for server to start
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            print("API server started successfully")
            print("   Server running at: http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print("Failed to start API server")
            if stderr:
                print(f"   Error: {stderr}")
            return None

    except Exception as e:
        print(f"Failed to start API server: {e}")
        return None


def open_frontend():
    """Open the frontend in default browser."""
    print("Opening frontend interface...")

    try:
        webbrowser.open("http://localhost:8000")
        print("Frontend opened in browser")
        return True
    except Exception as e:
        print(f"Could not auto-open browser: {e}")
        print("   Please manually open: http://localhost:8000")
        return False


def print_instructions():
    """Print usage instructions."""
    print()
    print("=" * 70)
    print("Veritas System Ready!")
    print("=" * 70)
    print()
    print("Frontend Interface: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print()
    print("Available Workflows:")
    print("   • Simple Pipeline:     Fast, linear research workflow")
    print("   • Enhanced Pipeline:   Multi-round reviews with version control")
    print("   • Domain-Adaptive:     Auto-configures for research domains")
    print()
    print("File Upload Support:")
    print("   • CSV files for data analysis")
    print("   • Excel files (.xlsx)")
    print("   • JSON data files")
    print()
    print("Important Notes:")
    print("   • Keep this terminal window open (server running)")
    print("   • Results saved to results/ directory")
    print("   • Press Ctrl+C to stop the server")
    print()
    print("Need help with API keys? Run: python setup_api_keys.py")
    print("=" * 70)


def main():
    """Main launcher function."""
    print_banner()

    # System checks
    if not check_python_version():
        sys.exit(1)

    if not check_environment():
        print("\nPlease configure API keys first:")
        print("   1. Run: python setup_api_keys.py")
        print("   2. Then run: python start_veritas.py")
        sys.exit(1)

    if not check_dependencies():
        print("\nPlease install dependencies first:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    print("\nAll system checks passed!")
    print()

    # Start the system
    server_process = start_api_server()
    if not server_process:
        print("Failed to start system")
        sys.exit(1)

    # Open frontend
    open_frontend()

    # Print instructions
    print_instructions()

    # Keep running and handle shutdown
    try:
        print("System running... Press Ctrl+C to stop")
        server_process.wait()
    except KeyboardInterrupt:
        print("\n\nShutting down Veritas system...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("System stopped cleanly")


if __name__ == "__main__":
    main()
