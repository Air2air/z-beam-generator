#!/usr/bin/env python3
"""
Network connectivity diagnostic tool for API endpoints
"""

import requests
import time
import socket
from urllib.parse import urlparse

def test_network_connectivity():
    """Test basic network connectivity to API endpoints"""

    endpoints = [
        "https://api.deepseek.com",
        "https://api.x.ai",
        "https://api.gowinston.ai"
    ]

    print("🌐 Network Connectivity Test")
    print("=" * 40)

    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")

        try:
            # Parse URL to get host and port
            parsed = urlparse(endpoint)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)

            # Test DNS resolution
            print(f"   📡 DNS Resolution: {host} -> ", end="")
            try:
                ip = socket.gethostbyname(host)
                print(f"✅ {ip}")
            except socket.gaierror as e:
                print(f"❌ Failed: {e}")
                continue

            # Test basic connectivity
            print(f"   🔌 Socket Connection: {host}:{port} -> ", end="")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                sock.connect((host, port))
                print("✅ Connected")
                sock.close()
            except socket.error as e:
                print(f"❌ Failed: {e}")
                continue

            # Test HTTP connectivity
            print(f"   🌐 HTTP Request: {endpoint}/v1/models -> ", end="")
            try:
                response = requests.get(f"{endpoint}/v1/models", timeout=10)
                print(f"✅ Status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed: {e}")

        except Exception as e:
            print(f"   💥 Unexpected error: {e}")

    print("\n📋 Network Test Complete")
    print("If all tests pass but API calls still fail, the issue may be:")
    print("   • API key authentication problems")
    print("   • Rate limiting by the API provider")
    print("   • Service outages or maintenance")
    print("   • Firewall or proxy blocking requests")

if __name__ == "__main__":
    test_network_connectivity()
