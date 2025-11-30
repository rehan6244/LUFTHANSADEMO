"""
Lufthansa Playwright Test - ML DATA GENERATION VERSION
This script runs the test and logs data for machine learning training.
"""
import re
import time
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright
from ml_logger import TestLogger

def test_lufthansa_ml(playwright: Playwright) -> None:
    # Initialize ML Logger
    logger = TestLogger()
    
    browser = playwright.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    print("=" * 70)
    print("LUFTHANSA ML DATA COLLECTION RUN")
    print("=" * 70)
    
    try:
        # STEP 1: Navigation
        start = time.time()
        try:
            page.goto("https://www.lufthansa.com/us/en/flight-search", wait_until="domcontentloaded")
            logger.log_step("Navigate to Home", "navigation", "url:flight-search", 1, "", (time.time()-start)*1000)
        except Exception as e:
            logger.log_step("Navigate to Home", "navigation", "url:flight-search", 0, str(e), (time.time()-start)*1000)
            raise e
            
        page.wait_for_timeout(3000)
        
        # STEP 2: Overlays
        start = time.time()
        try:
            page.evaluate("""
                () => {
                    document.querySelectorAll('button').forEach(btn => {
                        if (btn.textContent.toLowerCase().includes('agree')) btn.click();
                    });
                    ['consentOverlay', '__tealiumGDPRcpPrefs'].forEach(id => {
                        const el = document.getElementById(id);
                        if (el) el.remove();
                    });
                }
            """)
            logger.log_step("Handle Overlays", "javascript", "consent_buttons", 1, "", (time.time()-start)*1000)
        except Exception as e:
            logger.log_step("Handle Overlays", "javascript", "consent_buttons", 0, str(e), (time.time()-start)*1000)

        # STEP 3: Origin
        start = time.time()
        selector = "input[name*='originCode']"
        try:
            origin = page.locator(selector).first
            origin.click(force=True)
            origin.fill("")
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            origin.type("New York", delay=100)
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            logger.log_step("Set Origin", "input", selector, 1, "", (time.time()-start)*1000)
        except Exception as e:
            logger.log_step("Set Origin", "input", selector, 0, str(e), (time.time()-start)*1000)

        # STEP 4: Destination
        start = time.time()
        selector = "input[name*='destinationCode']"
        try:
            dest = page.locator(selector).first
            dest.click(force=True)
            dest.fill("")
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            dest.type("Berlin", delay=100)
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            logger.log_step("Set Destination", "input", selector, 1, "", (time.time()-start)*1000)
        except Exception as e:
            logger.log_step("Set Destination", "input", selector, 0, str(e), (time.time()-start)*1000)

        # STEP 5: Dates (The problematic part - good for ML to learn!)
        start = time.time()
        selector = "input[name*='travelDatetime']"
        try:
            # Try JS injection first (Success path)
            page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input[name*="travelDatetime"]');
                    if (inputs.length >= 2) {
                        inputs[0].value = '12/15/2025';
                        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[1].value = '12/25/2025';
                        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }
            """)
            # Try clicking calendar (Potential failure path)
            page.locator(selector).first.click(force=True)
            page.wait_for_timeout(1000)
            
            # Log this complex step
            logger.log_step("Select Dates", "complex_interaction", selector, 1, "", (time.time()-start)*1000)
        except Exception as e:
            logger.log_step("Select Dates", "complex_interaction", selector, 0, str(e), (time.time()-start)*1000)

        # STEP 6: Search
        start = time.time()
        selector = "button:has-text('Search flights')"
        try:
            page.locator(selector).first.click(force=True)
            logger.log_step("Click Search", "click", selector, 1, "", (time.time()-start)*1000)
        except Exception as e:
            logger.log_step("Click Search", "click", selector, 0, str(e), (time.time()-start)*1000)

        # STEP 7: Results
        start = time.time()
        selector = "div[class*='price']"
        try:
            page.wait_for_selector(selector, timeout=10000)
            logger.log_step("Wait for Results", "wait", selector, 1, "", (time.time()-start)*1000)
        except Exception as e:
            # This is where we expect failures if dates weren't set right
            logger.log_step("Wait for Results", "wait", selector, 0, "Timeout waiting for price elements", (time.time()-start)*1000)

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        context.close()
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        test_lufthansa_ml(playwright)
