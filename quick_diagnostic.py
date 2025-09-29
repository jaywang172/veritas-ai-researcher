#!/usr/bin/env python3
"""
Quick diagnostic script to check if Veritas is ready for execution
"""

from pathlib import Path

import requests


def check_server_status():
    """Check if the API server is running and ready."""
    try:
        response = requests.get("http://localhost:8000/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ API Server Status:")
            print(f"   - Running: {not status['is_running']}")
            print(f"   - Available workflows: {status['available_workflows']}")
            return True
        else:
            print(f"❌ Server responded with status {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to API server")
        print("   Make sure to run: python start_veritas.py")
        return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False


def check_data_file():
    """Check if the data file is accessible."""
    data_file = Path("sales_data.csv")
    if data_file.exists():
        print(f"✅ Data file found: {data_file}")
        print(f"   - Size: {data_file.stat().st_size:,} bytes")
        return True
    else:
        print(f"❌ Data file not found: {data_file}")
        return False


def test_file_upload():
    """Test file upload functionality."""
    try:
        data_file = Path("sales_data.csv")
        if not data_file.exists():
            print("❌ Cannot test upload - no data file")
            return False

        with open(data_file, "rb") as f:
            files = {"file": (data_file.name, f, "text/csv")}
            response = requests.post(
                "http://localhost:8000/api/upload", files=files, timeout=10
            )

        if response.status_code == 200:
            result = response.json()
            print("✅ File upload test successful:")
            print(f"   - Uploaded: {result['filename']}")
            print(f"   - Size: {result['size']:,} bytes")
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False


def main():
    """Run diagnostics."""
    print("Veritas System Diagnostics")
    print("=" * 50)

    # Check server
    server_ok = check_server_status()
    print()

    # Check data file
    data_ok = check_data_file()
    print()

    # Test upload if server is running
    upload_ok = False
    if server_ok:
        upload_ok = test_file_upload()
        print()

    # Summary
    print("=" * 50)
    print("DIAGNOSTICS SUMMARY")
    print("=" * 50)
    print(f"API Server: {'✅ READY' if server_ok else '❌ NOT READY'}")
    print(f"Data File: {'✅ READY' if data_ok else '❌ NOT READY'}")
    print(
        f"File Upload: {'✅ READY' if upload_ok else '❌ NOT TESTED' if not server_ok else '❌ FAILED'}"
    )
    print()

    if server_ok and data_ok:
        print("🎉 System is ready for research!")
        print()
        print("Next steps:")
        print("1. Open http://localhost:8000 in your browser")
        print("2. Select 'Enhanced Pipeline'")
        print("3. Paste your research goal")
        print("4. Upload sales_data.csv")
        print("5. Click 'Start Enhanced Research'")
        print()
        print("Your research goal:")
        print(
            "「基於sales_data.csv提供的五年期詳細財報，深度剖析NVIDIA商業模式的演變...」"
        )
    else:
        print("🔧 System needs setup:")
        if not server_ok:
            print("- Start the server: python start_veritas.py")
        if not data_ok:
            print("- Check that sales_data.csv exists in the project directory")


if __name__ == "__main__":
    main()
