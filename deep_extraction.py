"""
Deep extraction using multiple advanced techniques
"""

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
from bs4 import BeautifulSoup

def try_scorm_api_direct():
    """Try to access SCORM API directly"""
    print("\n1. TRYING DIRECT SCORM API ACCESS...")

    base_url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"

    # Try various SCORM API endpoints
    endpoints = [
        "api/scorm/",
        "scorm/",
        "lms/",
        "courses/",
        "content/",
        "data/",
        "manifest.xml",
        "imsmanifest.xml",
        "course.json",
        "structure.json",
        "js/courseStructure.js",
        "js/config.js",
        "js/pages.js"
    ]

    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            response = requests.get(url, verify=False, timeout=5)
            if response.status_code == 200:
                print(f"✓ Found: {url}")
                print(f"  Content preview: {response.text[:200]}")
        except:
            pass

def try_javascript_execution():
    """Execute JavaScript to extract course structure"""
    print("\n2. TRYING JAVASCRIPT EXECUTION...")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to main page
        driver.get("https://www.ptsd.va.gov/apps/CRAFTPTSD/")
        time.sleep(3)

        # Try to extract course structure from JavaScript
        js_commands = [
            # Look for global course objects
            "return window.course || window.Course || window.COURSE || {};",
            "return window.pages || window.Pages || window.PAGES || [];",
            "return window.lessons || window.Lessons || window.LESSONS || [];",
            "return window.modules || window.Modules || window.MODULES || [];",

            # Try to get from any framework
            "return window.courseData || window.courseStructure || {};",

            # Check for SCORM variables
            "return window.API ? Object.keys(window.API) : [];",
            "return window.scorm ? Object.keys(window.scorm) : [];",

            # Try to get navigation structure
            "return Array.from(document.querySelectorAll('[data-page]')).map(e => ({id: e.dataset.page, text: e.textContent}));",
            "return Array.from(document.querySelectorAll('[data-lesson]')).map(e => ({id: e.dataset.lesson, text: e.textContent}));",

            # Check localStorage and sessionStorage
            "return {...localStorage};",
            "return {...sessionStorage};",

            # Try to intercept navigation
            """
            if (window.navigation) {
                return window.navigation.entries().map(e => e.url);
            }
            return [];
            """
        ]

        for js in js_commands:
            try:
                result = driver.execute_script(js)
                if result and (isinstance(result, dict) and result != {} or isinstance(result, list) and result != []):
                    print(f"✓ Found data: {str(result)[:200]}")
            except Exception as e:
                pass

        # Try to navigate through pages programmatically
        print("\n3. TRYING PROGRAMMATIC NAVIGATION...")

        for page_id in [2, 3, 4, 5, 10, 15, 20]:  # Test problematic pages
            driver.get(f"https://www.ptsd.va.gov/apps/CRAFTPTSD/#/page/{page_id}")
            time.sleep(2)

            # Try multiple extraction methods
            extraction_js = """
            return {
                title: document.title,
                h1: document.querySelector('h1')?.textContent,
                h2: document.querySelector('h2')?.textContent,
                h3: document.querySelector('h3')?.textContent,
                bodyClasses: document.body.className,
                dataAttrs: Object.keys(document.body.dataset || {}),
                innerText: document.body.innerText?.substring(0, 200),
                // Try to get from any iframes
                iframeContent: (() => {
                    const iframe = document.querySelector('iframe');
                    if (iframe && iframe.contentDocument) {
                        return iframe.contentDocument.body?.innerText?.substring(0, 200);
                    }
                    return null;
                })(),
                // Check for hidden content
                hiddenDivs: Array.from(document.querySelectorAll('div[style*="display:none"], div[style*="visibility:hidden"]')).map(d => d.textContent?.substring(0, 50))
            };
            """

            result = driver.execute_script(extraction_js)
            if result.get('innerText') and len(result['innerText']) > 50:
                print(f"Page {page_id}: {result}")

    finally:
        driver.quit()

def try_iframe_content():
    """Check if content is in iframes"""
    print("\n4. CHECKING IFRAME CONTENT...")

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://www.ptsd.va.gov/apps/CRAFTPTSD/#/page/2")
        time.sleep(3)

        # Check for iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")

        for i, iframe in enumerate(iframes):
            try:
                # Get iframe source
                src = iframe.get_attribute('src')
                print(f"Iframe {i}: {src}")

                # Switch to iframe
                driver.switch_to.frame(iframe)

                # Get content
                content = driver.find_element(By.TAG_NAME, "body").text
                if content:
                    print(f"  Content: {content[:200]}")

                # Switch back
                driver.switch_to.default_content()
            except:
                driver.switch_to.default_content()

    finally:
        driver.quit()

def try_network_interception():
    """Use Chrome DevTools Protocol to intercept network"""
    print("\n5. TRYING NETWORK INTERCEPTION...")

    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('w3c', False)
    options.add_experimental_option('perfLoggingPrefs', {
        'enableNetwork': True,
        'enablePage': False,
    })

    driver = webdriver.Chrome(options=options, desired_capabilities=caps)

    try:
        # Enable Network domain
        driver.execute_cdp_cmd('Network.enable', {})

        # Set up request interception
        driver.execute_cdp_cmd('Network.setRequestInterception', {
            'patterns': [{'urlPattern': '*'}]
        })

        driver.get("https://www.ptsd.va.gov/apps/CRAFTPTSD/#/page/2")
        time.sleep(5)

        # Get performance logs
        logs = driver.get_log('performance')

        for entry in logs:
            obj = json.loads(entry['message'])['message']
            if 'Network.responseReceived' in obj['method']:
                response = obj['params']['response']
                if 'lesson' in response['url'] or 'content' in response['url']:
                    print(f"Response: {response['url']}")

                    # Try to get response body
                    try:
                        body = driver.execute_cdp_cmd('Network.getResponseBody', {
                            'requestId': obj['params']['requestId']
                        })
                        if body:
                            print(f"  Body: {body.get('body', '')[:200]}")
                    except:
                        pass

    finally:
        driver.quit()

def try_alternative_urls():
    """Try alternative URL patterns"""
    print("\n6. TRYING ALTERNATIVE URL PATTERNS...")

    patterns = [
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/index.html#page/{page_id}",
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/course/page{page_id}.html",
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/content/{page_id}",
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/pages/{page_id}",
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/#!/page/{page_id}",
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/#page={page_id}",
        "https://www.ptsd.va.gov/apps/CRAFTPTSD/?page={page_id}",
    ]

    test_pages = [2, 3, 4, 10]

    for pattern in patterns:
        for page_id in test_pages:
            url = pattern.format(page_id=page_id)
            try:
                response = requests.get(url, verify=False, timeout=3)
                if response.status_code == 200 and len(response.text) > 500:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Remove scripts and styles
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    if 'requires frames' not in text and len(text) > 100:
                        print(f"✓ Working pattern: {pattern}")
                        print(f"  Page {page_id} content: {text[:100]}")
                        break
            except:
                pass

if __name__ == "__main__":
    print("DEEP EXTRACTION ATTEMPT")
    print("=" * 70)

    try_scorm_api_direct()
    try_javascript_execution()
    try_iframe_content()
    try_network_interception()
    try_alternative_urls()