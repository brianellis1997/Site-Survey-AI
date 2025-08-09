#!/usr/bin/env python3

import requests
import time
import subprocess
import sys
import os

def test_api():
    """Test the simplified API"""
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint  
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - make sure it's running")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Site Survey AI API...")
    success = test_api()
    sys.exit(0 if success else 1)