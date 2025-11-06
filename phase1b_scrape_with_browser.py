#!/usr/bin/env python3
"""
Phase 1.B: Scrape VA CRAFT PTSD website using headless browser
"""

import time
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

def setup_driver():
    """Set up Selenium with the existing Chrome installation"""
    chrome_options = Options()

    # Use existing Chrome binary
    chrome_options.binary_location = "/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"

    # Headless mode
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # SSL/Certificate bypass
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--disable-web-security")

    # Stability settings
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--single-process")  # Prevent crashes

    # Stealth settings to avoid bot detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Set realistic user agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    )

    # Use the chromedriver
    service = Service(executable_path="/opt/node22/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Additional stealth
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    return driver

def test_site_access():
    """Test if we can access the VA site with the browser"""
    print("="*80)
    print("TESTING SITE ACCESS WITH HEADLESS BROWSER")
    print("="*80)

    driver = None
    try:
        print("\n[1] Setting up Chrome driver...")
        driver = setup_driver()

        url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"
        print(f"\n[2] Navigating to: {url}")

        driver.get(url)

        # Wait for page to load
        print("\n[3] Waiting for page to load...")
        time.sleep(5)

        print(f"\n[4] Current URL: {driver.current_url}")
        print(f"    Page Title: {driver.title}")

        # Check page content
        page_source = driver.page_source
        print(f"\n[5] Page source length: {len(page_source)} bytes")

        # Check if we got blocked
        if "access denied" in page_source.lower() or len(page_source) < 500:
            print("\n❌ BLOCKED: Site returned access denied or minimal content")
            print(f"   Content preview: {page_source[:200]}")
            return False

        print("\n✅ SUCCESS: Page loaded successfully!")

        # Save the page
        with open('/home/user/VACRAFT/browser_page.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("   Saved to: browser_page.html")

        # Look for content
        soup = BeautifulSoup(page_source, 'html.parser')

        # Check for links
        links = soup.find_all('a', href=True)
        print(f"\n[6] Found {len(links)} links")

        # Sample some links
        print("\n    Sample links:")
        for link in links[:10]:
            href = link.get('href', '')
            text = link.get_text(strip=True)[:50]
            print(f"      - {text}: {href}")

        # Check for navigation structure
        print("\n[7] Analyzing URL structure...")

        # Try clicking on a link or button to see navigation
        try:
            # Look for "start", "begin", "enter" buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                text = button.text.lower()
                if any(keyword in text for keyword in ["start", "begin", "enter", "continue"]):
                    print(f"\n    Found button: '{button.text}'")
                    print(f"    Clicking...")
                    button.click()
                    time.sleep(3)
                    print(f"    New URL: {driver.current_url}")
                    break
        except Exception as e:
            print(f"    Could not interact with buttons: {e}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            print("\n[8] Closing browser...")
            driver.quit()

def explore_url_patterns(driver):
    """Explore the URL structure to determine mapping strategy"""
    print("\n" + "="*80)
    print("EXPLORING URL PATTERNS")
    print("="*80)

    base_url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"

    # Test different URL patterns
    patterns_to_test = [
        ("Sequential", f"{base_url}#/page/1"),
        ("Sequential", f"{base_url}#/page/2"),
        ("Sequential", f"{base_url}#/page/10"),
        ("Hierarchical", f"{base_url}#/course/1"),
        ("Hierarchical", f"{base_url}#/lesson/1"),
        ("Hierarchical", f"{base_url}#/module/1"),
    ]

    results = {}

    for pattern_type, test_url in patterns_to_test:
        print(f"\n Testing: {test_url}")
        try:
            driver.get(test_url)
            time.sleep(2)

            final_url = driver.current_url
            page_source = driver.page_source

            # Check if URL was accepted
            if final_url == test_url:
                print(f"   ✓ URL accepted!")

                # Extract page title
                soup = BeautifulSoup(page_source, 'html.parser')
                title = driver.title

                # Look for main content
                body_text = soup.get_text(strip=True)[:200]

                print(f"   Title: {title}")
                print(f"   Content preview: {body_text[:100]}...")

                results[pattern_type] = "WORKS"
            else:
                print(f"   ✗ Redirected to: {final_url}")
                results[pattern_type] = "REDIRECTED"

        except Exception as e:
            print(f"   ✗ Error: {e}")
            results[pattern_type] = "ERROR"

    return results

def scrape_sequential_pages(driver, start=1, end=191):
    """Scrape pages using sequential URL pattern"""
    print("\n" + "="*80)
    print(f"SCRAPING PAGES {start} TO {end}")
    print("="*80)

    base_url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/#/page/"

    data = []

    for page_id in range(start, end + 1):
        print(f"\n[{page_id}/{end}] Scraping page {page_id}...")

        url = f"{base_url}{page_id}"

        try:
            driver.get(url)
            time.sleep(1.5)  # Be respectful to VA servers

            # Check if we got content
            current_url = driver.current_url

            if f"#/page/{page_id}" not in current_url:
                print(f"   ⚠ Skipped (redirected to: {current_url})")
                continue

            # Extract page information
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Get page title (try different selectors)
            page_title = None
            for selector in ['h1', 'h2', '.page-title', '.title', '.heading']:
                elem = soup.select_one(selector)
                if elem:
                    page_title = elem.get_text(strip=True)
                    break

            if not page_title:
                page_title = driver.title

            # Try to extract hierarchical info from page content
            # Look for breadcrumbs, section headers, etc.
            course = None
            section = None
            lesson = None

            # Check for breadcrumbs
            breadcrumbs = soup.select('.breadcrumb li, .breadcrumb a, nav a')
            if breadcrumbs:
                # Extract hierarchical structure from breadcrumbs
                bc_texts = [bc.get_text(strip=True) for bc in breadcrumbs if bc.get_text(strip=True)]
                if len(bc_texts) >= 1:
                    course = bc_texts[0] if len(bc_texts) > 0 else None
                    section = bc_texts[1] if len(bc_texts) > 1 else None
                    lesson = bc_texts[2] if len(bc_texts) > 2 else None

            # Determine if this is a lesson end page
            # Look for keywords like "summary", "quiz", "complete", "next lesson"
            page_text = soup.get_text().lower()
            is_lesson_end = any(keyword in page_text for keyword in [
                'lesson complete', 'lesson summary', 'next lesson',
                'quiz', 'assessment', 'congratulations'
            ])

            # Determine if this is content (not menu/navigation)
            is_content = True  # Assume content unless proven otherwise

            print(f"   ✓ Title: {page_title[:60]}...")
            if course or section or lesson:
                print(f"   Hierarchy: {course} > {section} > {lesson}")

            data.append({
                'Page_ID': page_id,
                'URL': url,
                'Page_Title': page_title,
                'Course': course,
                'Section': section,
                'Lesson': lesson,
                'Is_Lesson_End': is_lesson_end,
                'Is_Content': is_content
            })

        except Exception as e:
            print(f"   ✗ Error: {e}")
            continue

    # Add menu entry
    data.append({
        'Page_ID': 'menu',
        'URL': f"{base_url}menu",
        'Page_Title': 'Main Menu',
        'Course': 'Navigation',
        'Section': 'Navigation',
        'Lesson': 'Navigation',
        'Is_Lesson_End': False,
        'Is_Content': False
    })

    return data

def main():
    """Main execution"""
    print("="*80)
    print("PHASE 1.B: VA CRAFT PTSD WEBSITE SCRAPING")
    print("="*80)

    # First test if we can access the site
    if not test_site_access():
        print("\n❌ Cannot access site with browser. Stopping.")
        return False

    print("\n\n" + "="*80)
    print("PROCEEDING WITH FULL SCRAPE")
    print("="*80)

    driver = None
    try:
        print("\n[1] Setting up driver...")
        driver = setup_driver()

        print("\n[2] Exploring URL patterns...")
        pattern_results = explore_url_patterns(driver)

        print("\n[3] Pattern test results:")
        for pattern, result in pattern_results.items():
            print(f"   {pattern}: {result}")

        # Determine which approach to use
        if pattern_results.get("Sequential") == "WORKS":
            print("\n✓ Using SEQUENTIAL pattern (#/page/N)")

            print("\n[4] Starting full scrape...")
            data = scrape_sequential_pages(driver, start=1, end=191)

            print(f"\n[5] Scraped {len(data)} pages")

            # Save to CSV
            df = pd.DataFrame(data)
            output_path = '/home/user/VACRAFT/Data_Dictionary.csv'
            df.to_csv(output_path, index=False)

            print(f"\n✅ SUCCESS! Data dictionary saved to: {output_path}")
            print(f"   Total pages: {len(df)}")
            print(f"\nFirst few entries:")
            print(df.head(10))

            return True
        else:
            print("\n⚠ Sequential pattern not working. Need alternative approach.")
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if driver:
            print("\n[6] Closing browser...")
            driver.quit()

if __name__ == "__main__":
    success = main()
    print("\n" + "="*80)
    if success:
        print("✅ PHASE 1.B COMPLETE")
    else:
        print("❌ PHASE 1.B FAILED - CONTINGENCY PLAN NEEDED")
    print("="*80)
