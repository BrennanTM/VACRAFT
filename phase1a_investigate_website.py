#!/usr/bin/env python3
"""
Phase 1.A: Website Investigation
Determine the URL structure and mapping strategy for the VA CRAFT PTSD course
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def investigate_website():
    """
    Navigate the VA CRAFT PTSD website to determine URL structure
    """
    print("=" * 80)
    print("PHASE 1.A: WEBSITE INVESTIGATION")
    print("=" * 80)

    # Set up Selenium with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = None

    try:
        print("\n[1] Initializing browser...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)

        # Navigate to the main page
        url = "https://www.ptsd.va.gov/apps/CRAFTPTSD/"
        print(f"\n[2] Navigating to: {url}")
        driver.get(url)

        # Wait for the page to load
        time.sleep(3)

        print(f"\n[3] Initial URL after load: {driver.current_url}")
        print(f"    Page Title: {driver.title}")

        # Check if there's a redirect or hash routing
        current_url = driver.current_url

        # Try to find navigation elements or links to explore the structure
        print("\n[4] Analyzing page structure...")

        # Look for common navigation patterns
        try:
            # Check for links or buttons that might navigate to content pages
            links = driver.find_elements(By.TAG_NAME, "a")
            print(f"    Found {len(links)} link elements")

            # Sample a few links to see URL patterns
            sample_hrefs = []
            for i, link in enumerate(links[:10]):
                try:
                    href = link.get_attribute("href")
                    if href:
                        sample_hrefs.append(href)
                except:
                    pass

            if sample_hrefs:
                print("\n    Sample URLs found on page:")
                for href in sample_hrefs[:5]:
                    print(f"      - {href}")
        except Exception as e:
            print(f"    Error analyzing links: {e}")

        # Try to click on a "start" or "begin" button
        print("\n[5] Looking for course entry points...")

        entry_keywords = ["start", "begin", "continue", "enter", "login", "get started"]
        clicked = False

        for keyword in entry_keywords:
            if clicked:
                break
            try:
                # Try buttons first
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        text = button.text.lower()
                        if keyword in text:
                            print(f"    Found button with text: '{button.text}'")
                            button.click()
                            clicked = True
                            time.sleep(3)
                            print(f"    New URL after click: {driver.current_url}")
                            break
                    except:
                        pass

                # Try links
                if not clicked:
                    links = driver.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        try:
                            text = link.text.lower()
                            if keyword in text:
                                print(f"    Found link with text: '{link.text}'")
                                link.click()
                                clicked = True
                                time.sleep(3)
                                print(f"    New URL after click: {driver.current_url}")
                                break
                        except:
                            pass
            except Exception as e:
                pass

        if not clicked:
            print("    No obvious entry point found, examining current page...")

        # Now try to test URL patterns
        print("\n[6] Testing URL patterns...")

        current_url = driver.current_url

        # Scenario A: Sequential URLs (e.g., /#/page/1)
        print("\n    Testing Scenario A (Sequential URLs)...")
        test_urls = [
            f"{url}#/page/1",
            f"{url}#/page/2",
            f"{url}#/page/117"
        ]

        for test_url in test_urls:
            try:
                print(f"      Testing: {test_url}")
                driver.get(test_url)
                time.sleep(2)

                # Check if page loaded successfully
                if driver.current_url == test_url:
                    print(f"        ✓ URL accepted: {driver.current_url}")

                    # Try to extract page content
                    try:
                        page_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                        print(f"        Sample content: {page_text[:100]}...")
                    except:
                        pass
                else:
                    print(f"        ✗ Redirected to: {driver.current_url}")
            except Exception as e:
                print(f"        ✗ Error: {e}")

        # Scenario B: Hierarchical URLs (e.g., /#/course/1/lesson/2/page/1)
        print("\n    Testing Scenario B (Hierarchical URLs)...")
        test_urls = [
            f"{url}#/course/1",
            f"{url}#/course/1/lesson/1",
            f"{url}#/course/1/lesson/1/page/1",
            f"{url}#/module/1",
            f"{url}#/lesson/1"
        ]

        for test_url in test_urls:
            try:
                print(f"      Testing: {test_url}")
                driver.get(test_url)
                time.sleep(2)

                if driver.current_url == test_url:
                    print(f"        ✓ URL accepted: {driver.current_url}")

                    # Try to extract page content
                    try:
                        page_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                        print(f"        Sample content: {page_text[:100]}...")
                    except:
                        pass
                else:
                    print(f"        ✗ Redirected to: {driver.current_url}")
            except Exception as e:
                print(f"        ✗ Error: {e}")

        # Inspect the page source for clues
        print("\n[7] Inspecting page source for routing hints...")

        page_source = driver.page_source

        # Look for Angular, React, Vue patterns
        if "ng-app" in page_source or "angular" in page_source.lower():
            print("    Detected: Likely Angular application")
        if "react" in page_source.lower():
            print("    Detected: Likely React application")
        if "vue" in page_source.lower():
            print("    Detected: Likely Vue application")

        # Look for route definitions or page IDs in the source
        if "#/page/" in page_source:
            print("    Found: '#/page/' pattern in source (Sequential routing)")
        if "#/lesson/" in page_source:
            print("    Found: '#/lesson/' pattern in source (Hierarchical routing)")

        # Final URL analysis
        print("\n[8] SUMMARY OF FINDINGS:")
        print("=" * 80)
        print(f"Current URL: {driver.current_url}")

        current = driver.current_url

        if "#/page/" in current:
            print("\n✓ SCENARIO A DETECTED: Sequential URL pattern")
            print("  Strategy: Iterate through sequential page numbers in URLs")
            print("  Example: /#/page/1, /#/page/2, /#/page/3, etc.")
            return "SCENARIO_A"

        elif "#/course/" in current or "#/lesson/" in current or "#/module/" in current:
            print("\n✓ SCENARIO B DETECTED: Hierarchical URL pattern")
            print("  Strategy: Navigate hierarchically and extract sequential IDs from page content")
            print("  Example: /#/course/1/lesson/2/page/1")
            return "SCENARIO_B"

        else:
            print("\n⚠ SCENARIO UNKNOWN: Further investigation needed")
            print("  Current URL structure not matching expected patterns")
            print("  May require manual inspection or alternative approach")
            return "UNKNOWN"

    except Exception as e:
        print(f"\n✗ ERROR during investigation: {e}")
        import traceback
        traceback.print_exc()
        return "ERROR"

    finally:
        if driver:
            print("\n[9] Closing browser...")
            driver.quit()

if __name__ == "__main__":
    scenario = investigate_website()
    print("\n" + "=" * 80)
    print(f"DETECTED SCENARIO: {scenario}")
    print("=" * 80)
