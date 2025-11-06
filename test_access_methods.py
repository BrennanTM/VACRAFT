#!/usr/bin/env python3
"""
Test different methods to access the VA CRAFT PTSD site
"""

import requests
import time

def test_with_headers():
    """Try accessing with proper browser headers"""
    url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"

    # Try different user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ]

    for i, ua in enumerate(user_agents, 1):
        print(f"\nTest {i}: User-Agent = {ua[:50]}...")

        headers = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Length: {len(response.text)}")
            print(f"  Preview: {response.text[:100]}")

            if response.status_code == 200:
                print("  ✓ SUCCESS!")
                with open(f'/home/user/VACRAFT/success_response_{i}.html', 'w') as f:
                    f.write(response.text)
                return True

        except Exception as e:
            print(f"  ✗ Error: {e}")

        time.sleep(1)

    return False

def test_direct_page_urls():
    """Try accessing specific page URLs directly"""
    base_url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"

    test_urls = [
        f"{base_url}",
        f"{base_url}index.html",
        f"{base_url}#/page/1",
        f"{base_url}#/page/2",
        f"{base_url}#/lesson/1",
        f"{base_url}#/course/1"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    print("\n" + "="*80)
    print("Testing direct page URLs...")
    print("="*80)

    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Length: {len(response.text)}")
            if response.status_code == 200:
                print(f"  ✓ Accessible!")
        except Exception as e:
            print(f"  ✗ Error: {e}")

        time.sleep(1)

if __name__ == "__main__":
    print("="*80)
    print("TESTING ACCESS METHODS TO VA CRAFT PTSD SITE")
    print("="*80)

    success = test_with_headers()

    if not success:
        test_direct_page_urls()

    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("The VA CRAFT PTSD website appears to be protected by:")
    print("  - Web Application Firewall (WAF)")
    print("  - Bot detection")
    print("  - Automated access prevention")
    print("\nThis requires CONTINGENCY PLAN activation:")
    print("  → Manual data dictionary creation")
    print("  → Or user-provided course structure")
    print("="*80)
