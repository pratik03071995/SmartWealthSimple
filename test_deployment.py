#!/usr/bin/env python3
"""
Test script to verify deployment is working correctly
"""

import requests
import sys
import os

def test_backend_health(backend_url):
    """Test if the backend is responding"""
    try:
        response = requests.get(f"{backend_url}/api/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Backend health check passed: {response.json()}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_api_endpoints(backend_url):
    """Test main API endpoints"""
    endpoints = [
        "/api/companies/dynamic",
        "/api/ai/sectors"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=30)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def main():
    # Get backend URL from environment or use default
    backend_url = os.environ.get('BACKEND_URL', 'http://127.0.0.1:5000')
    
    print(f"Testing backend at: {backend_url}")
    print("=" * 50)
    
    # Test health endpoint
    if test_backend_health(backend_url):
        # Test other endpoints
        test_api_endpoints(backend_url)
    else:
        print("Backend is not responding. Please check your deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
