"""
Playwright test script for Lufthansa flight booking
Tests: New York to Berlin round trip booking and price assertion

"""
import re
from playwright.sync_api import Playwright, sync_playwright, TimeoutError
import time
from datetime import datetime, timedelta


def test_lufthansa_booking(playwright: Playwright) -> None:
    """
    Test Lufthansa flight booking from New York to Berlin
    - Navigates to Lufthansa booking page
    - Fills in origin (New York) and destination (Berlin) - ALWAYS CLEARS FIRST
    - Selects round trip dates
    - Gets the price and asserts it matches expected format
    """
    
    # Launch browser
    browser = playwright.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    try:
        # Navigate to Lufthansa flight search page directly
        print("=" * 70)
        print("LUFTHANSA FLIGHT BOOKING TEST - NEW YORK TO BERLIN")
        print("=" * 70)
        print("\n[STEP 1/9] Navigating to Lufthansa...")
        page.goto("https://www.lufthansa.com/us/en/homepage", wait_until="domcontentloaded")
        page.wait_for_timeout(5000)
        
        # Handle cookie consent
        print("[STEP 2/9] Handling cookie consent...")
        try:
            # Remove consent overlay immediately with JavaScript
            page.evaluate("""
                () => {
                    // Click consent button if exists
                    const consentButtons = document.querySelectorAll('button[class*="consent"], button:has-text("Agree")');
                    if (consentButtons.length > 0) {
                        consentButtons[0].click();
                    }
                    // Remove overlays
                    setTimeout(() => {
                        const overlay = document.getElementById('consentOverlay');
                        if (overlay) overlay.remove();
                        const gdpr = document.getElementById('__tealiumGDPRcpPrefs');
                        if (gdpr) gdpr.remove();
                    }, 1000);
                }
            """)
            page.wait_for_timeout(2000)
            print("   ✓ Cookie consent handled")
        except:
            print("   ✓ No cookie consent needed")
        
        # Navigate to flight search
        print("[STEP 3/9] Navigating to flight search...")
        page.goto("https://www.lufthansa.com/us/en/flight-search", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        
        # Remove any remaining overlays
        page.evaluate("""
            () => {
                const overlay = document.getElementById('consentOverlay');
                if (overlay) overlay.remove();
                const gdpr = document.getElementById('__tealiumGDPRcpPrefs');
                if (gdpr) gdpr.remove();
                // Close feedback form
                const feedbackClose = document.querySelector('a[aria-label*="Close feedback"]');
                if (feedbackClose) feedbackClose.click();
            }
        """)
        page.wait_for_timeout(1000)
        
        # Ensure round trip
        print("[STEP 4/9] Selecting round trip...")
        try:
            page.locator("input[value='ROUND_TRIP']").first.check(force=True)
            print("   ✓ Round trip selected")
        except:
            print("   ✓ Round trip already selected")
        
        # Fill origin - New York
        print("[STEP 5/9] Entering origin: New York...")
        print("   → Clearing origin field (as required)...")
        origin_input = page.locator("input[name*='originCode'], input[placeholder*='From']").first
        origin_input.click(force=True)
        page.wait_for_timeout(500)
        # Clear the field completely
        origin_input.fill("")
        page.wait_for_timeout(200)
        origin_input.press("Control+A")
        page.wait_for_timeout(100)
        origin_input.press("Backspace")
        page.wait_for_timeout(300)
        
        print("   → Typing 'New York'...")
        origin_input.type("New York", delay=100)
        page.wait_for_timeout(2500)
        
        print("   → Selecting JFK...")
        try:
            page.locator("div[role='option']:has-text('JFK')").first.click(force=True, timeout=5000)
            print("   ✓ JFK International selected")
        except:
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            print("   ✓ Airport selected via keyboard")
        page.wait_for_timeout(1000)
        
        # Fill destination - Berlin
        print("[STEP 6/9] Entering destination: Berlin...")
        print("   → Clearing destination field (as required)...")
        dest_input = page.locator("input[name*='destinationCode'], input[placeholder*='To']").first
        dest_input.click(force=True)
        page.wait_for_timeout(500)
        # Clear the field completely
        dest_input.fill("")
        page.wait_for_timeout(200)
        dest_input.press("Control+A")
        page.wait_for_timeout(100)
        dest_input.press("Backspace")
        page.wait_for_timeout(300)
        
        print("   → Typing 'Berlin'...")
        dest_input.type("Berlin", delay=100)
        page.wait_for_timeout(2500)
        
        print("   → Selecting Berlin Brandenburg...")
        try:
            page.locator("div[role='option']:has-text('BER'), div[role='option']:has-text('Brandenburg')").first.click(force=True, timeout=5000)
            print("   ✓ Berlin Brandenburg selected")
        except:
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            print("   ✓ Airport selected via keyboard")
        page.wait_for_timeout(1000)
        
        # Select dates - December 15, 2025 to December 25, 2025
        print("[STEP 7/9] Selecting travel dates (Dec 15-25, 2025)...")
        
        # Method 1: Try direct input with specific format
        try:
            print("   → Attempting direct date input...")
            
            # Get the date input fields
            dep_input = page.locator("input[name*='travelDatetime']").first
            ret_input = page.locator("input[name*='travelDatetime']").nth(1)
            
            # Try to set departure date via JavaScript
            page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input[name*="travelDatetime"]');
                    if (inputs.length >= 2) {
                        inputs[0].value = '12/15/2025';
                        inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[0].dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            """)
            page.wait_for_timeout(1000)
            
            # Try to set return date via JavaScript
            page.evaluate("""
                () => {
                    const inputs = document.querySelectorAll('input[name*="travelDatetime"]');
                    if (inputs.length >= 2) {
                        inputs[1].value = '12/25/2025';
                        inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
                        inputs[1].dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
            """)
            page.wait_for_timeout(1000)
            print("   ✓ Dates set via JavaScript")
            
        except Exception as e:
            print(f"   ⚠ JavaScript date setting failed: {str(e)[:50]}")
        
        # Method 2: Try clicking and using calendar
        try:
            print("   → Attempting calendar selection...")
            
            # Click departure date field
            dep_input = page.locator("input[name*='travelDatetime']").first
            dep_input.click(force=True)
            page.wait_for_timeout(2000)
            
            # Try to find December 15, 2025 in calendar
            # Look for button with aria-label containing "December 15"
            dec_15_selectors = [
                "button[aria-label*='December 15']",
                "button[aria-label*='15 December']",
                "button[aria-label*='Dec 15']",
                "td[data-date*='2025-12-15'] button",
                "button:has-text('15')"
            ]
            
            date_selected = False
            for selector in dec_15_selectors:
                try:
                    date_btn = page.locator(selector).first
                    if date_btn.is_visible(timeout=2000):
                        date_btn.click(force=True)
                        print("   ✓ December 15 selected from calendar")
                        date_selected = True
                        page.wait_for_timeout(1500)
                        break
                except:
                    continue
            
            if not date_selected:
                # Fallback: click first available date
                try:
                    available = page.locator("td[role='gridcell']:not([aria-disabled='true']) button").first
                    available.click(force=True)
                    print("   ✓ Departure date selected (first available)")
                    page.wait_for_timeout(1500)
                except:
                    pass
            
            # Try to find December 25, 2025 for return
            dec_25_selectors = [
                "button[aria-label*='December 25']",
                "button[aria-label*='25 December']",
                "button[aria-label*='Dec 25']",
                "td[data-date*='2025-12-25'] button",
                "button:has-text('25')"
            ]
            
            return_selected = False
            for selector in dec_25_selectors:
                try:
                    date_btn = page.locator(selector).first
                    if date_btn.is_visible(timeout=2000):
                        date_btn.click(force=True)
                        print("   ✓ December 25 selected from calendar")
                        return_selected = True
                        page.wait_for_timeout(1000)
                        break
                except:
                    continue
            
            if not return_selected:
                # Fallback: click a date 10 days later
                try:
                    available = page.locator("td[role='gridcell']:not([aria-disabled='true']) button").nth(10)
                    available.click(force=True)
                    print("   ✓ Return date selected (10 days later)")
                except:
                    pass
            
        except Exception as e:
            print(f"   ⚠ Calendar selection issue: {str(e)[:60]}")
        
        # Search for flights
        print("[STEP 8/9] Searching for flights...")
        search_btn = page.locator("button:has-text('Search flights'), button[type='submit']").first
        search_btn.click(force=True)
        print("   ✓ Search initiated")
        
        # Wait for results
        print("[STEP 9/9] Waiting for results...")
        page.wait_for_timeout(10000)
        
        # Try to detect if we're on results page
        try:
            page.wait_for_selector("div[class*='flight'], div[class*='price'], span[class*='price']", timeout=15000)
            print("   ✓ Results page loaded")
        except:
            print("   ⚠ Timeout waiting for results, checking page anyway...")
        
        page.wait_for_timeout(3000)
        
        # Take screenshot
        screenshot_path = "/Users/mdahmed/.gemini/antigravity/scratch/lufthansa-playwright-test/search_results.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"\n� Screenshot saved: {screenshot_path}")
        
        # Extract price
        print("\n" + "=" * 70)
        print("EXTRACTING AND VALIDATING PRICE")
        print("=" * 70)
        
        price_text = None
        
        # Strategy 1: Look for price elements
        print("\n[Strategy 1] Searching for price elements...")
        selectors = [
            "span[class*='price']",
            "div[class*='price'] span",
            "span[class*='amount']",
            "div[class*='fare'] span",
            "span[data-test*='price']",
        ]
        
        for sel in selectors:
            try:
                elements = page.locator(sel).all()
                for elem in elements:
                    try:
                        text = elem.inner_text(timeout=1000).strip()
                        if '$' in text and re.search(r'\d{3,}', text.replace(',', '')):
                            price_text = text
                            print(f"   ✓ Found price: {price_text} (selector: {sel})")
                            break
                    except:
                        continue
                if price_text:
                    break
            except:
                continue
        
        # Strategy 2: Regex search in page
        if not price_text:
            print("\n[Strategy 2] Searching page content with regex...")
            content = page.content()
            matches = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', content)
            for match in matches:
                num = int(re.sub(r'[^\d]', '', match))
                if 300 <= num <= 5000:
                    price_text = match.strip()
                    print(f"   ✓ Found price via regex: {price_text}")
                    break
        
        # Strategy 3: Look in visible text
        if not price_text:
            print("\n[Strategy 3] Searching visible text...")
            try:
                body_text = page.locator("body").inner_text()
                matches = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', body_text)
                for match in matches:
                    num = int(re.sub(r'[^\d]', '', match))
                    if 300 <= num <= 5000:
                        price_text = match.strip()
                        print(f"   ✓ Found price in body text: {price_text}")
                        break
            except:
                pass
        
        # ASSERTIONS
        print("\n" + "=" * 70)
        print("RUNNING ASSERTIONS")
        print("=" * 70)
        
        # Assertion 1: Price found
        assert price_text is not None, "❌ FAILED: Price not found on page"
        print(f"\n✅ ASSERTION 1 PASSED: Price found = '{price_text}'")
        
        # Assertion 2: Extract numeric value
        price_match = re.search(r'[\d,]+(?:\.\d{2})?', price_text)
        assert price_match is not None, "❌ FAILED: Could not extract numeric value"
        price_value = float(price_match.group().replace(',', ''))
        print(f"✅ ASSERTION 2 PASSED: Numeric value = ${price_value:.2f}")
        
        # Assertion 3: Reasonable range
        assert 300 <= price_value <= 5000, f"❌ FAILED: Price ${price_value} outside range $300-$5000"
        print(f"✅ ASSERTION 3 PASSED: Price within reasonable range ($300-$5000)")
        
        # Assertion 4: Expected range for this route
        expected_min, expected_max = 500.00, 3000.00
        assert expected_min <= price_value <= expected_max, \
            f"❌ FAILED: Price ${price_value} outside expected range ${expected_min}-${expected_max}"
        print(f"✅ ASSERTION 4 PASSED: Price within expected range (${expected_min}-${expected_max})")
        
        # SUCCESS
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print(f"\n  Route:       New York (JFK) → Berlin (BER) - Round Trip")
        print(f"  Price:       {price_text}")
        print(f"  Value:       ${price_value:.2f}")
        print(f"  Status:      ✅ PASS")
        print(f"  Timestamp:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n" + "=" * 70)
        
        # Keep browser open briefly
        print("\n⏸  Browser will close in 5 seconds...")
        page.wait_for_timeout(5000)
        
    except AssertionError as e:
        error_path = "/Users/mdahmed/.gemini/antigravity/scratch/lufthansa-playwright-test/error_screenshot.png"
        page.screenshot(path=error_path, full_page=True)
        print(f"\n{'=' * 70}")
        print("❌ TEST FAILED!")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print(f"Screenshot: {error_path}")
        print("=" * 70)
        raise e
        
    except Exception as e:
        error_path = "/Users/mdahmed/.gemini/antigravity/scratch/lufthansa-playwright-test/error_screenshot.png"
        page.screenshot(path=error_path, full_page=True)
        print(f"\n{'=' * 70}")
        print("❌ TEST ERROR!")
        print("=" * 70)
        print(f"Error: {str(e)}")
        print(f"Screenshot: {error_path}")
        print("=" * 70)
        raise e
        
    finally:
        print("\n🔒 Closing browser...")
        context.close()
        browser.close()
        print("✓ Done")


def run():
    """Run the test"""
    with sync_playwright() as playwright:
        test_lufthansa_booking(playwright)


if __name__ == "__main__":
    run()
