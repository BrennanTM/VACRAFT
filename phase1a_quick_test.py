#!/usr/bin/env python3
"""
Quick test to see if the VA CRAFT PTSD site requires JavaScript
"""

import requests
from bs4 import BeautifulSoup

def quick_test():
    """Test if we can access the site without JavaScript"""
    url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"

    print("Testing basic HTTP access to VA CRAFT PTSD site...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
        print(f"Content Length: {len(response.text)} bytes")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for common SPA indicators
        print("\n--- Content Analysis ---")

        # Check for root div
        root_elements = soup.find_all(['div'], {'id': ['root', 'app', 'ng-app']})
        if root_elements:
            print(f"Found root element(s): {[elem.get('id') for elem in root_elements]}")

        # Check for Angular/React/Vue
        html_tag = soup.find('html')
        if html_tag:
            print(f"HTML attributes: {html_tag.attrs}")

        # Check for script tags
        scripts = soup.find_all('script')
        print(f"Number of script tags: {len(scripts)}")

        # Look for navigation or content
        links = soup.find_all('a', href=True)
        print(f"Number of links: {len(links)}")

        # Sample some links
        print("\nSample links found:")
        for link in links[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  - {text[:50]}: {href[:100]}")

        # Check if there's any meaningful text content
        body_text = soup.get_text(strip=True)
        print(f"\nBody text length: {len(body_text)} characters")
        print(f"Sample text: {body_text[:200]}...")

        # Save the HTML for inspection
        with open('/home/user/VACRAFT/initial_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\nSaved page HTML to: initial_page.html")

        # Decision
        print("\n--- Assessment ---")
        if len(body_text) < 500 or 'ng-app' in str(html_tag) or soup.find('div', {'id': 'root'}):
            print("⚠ Site appears to be a JavaScript-based SPA")
            print("  → Need Selenium/browser automation")
            return "NEEDS_SELENIUM"
        else:
            print("✓ Site may be accessible without JavaScript")
            print("  → Can try direct HTTP requests")
            return "DIRECT_ACCESS"

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

if __name__ == "__main__":
    result = quick_test()
    print(f"\n{'='*80}")
    print(f"RESULT: {result}")
    print(f"{'='*80}")
