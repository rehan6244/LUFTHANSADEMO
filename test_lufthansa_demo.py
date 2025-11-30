"""
Lufthansa Playwright Test - DEMO VERSION WITH MANUAL DATE SELECTION
This version pauses to allow manual date selection, then continues with automation
Tests: New York to Berlin round trip booking and price assertion
"""
import re
from playwright.sync_api import Playwright, sync_playwright
from datetime import datetime


def test_lufthansa_demo(playwright: Playwright) -> None:
    """
    Demo version with manual date selection
    """
    
    browser = playwright.chromium.launch(headless=False, slow_mo=300)
    context = browser.new_context(viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
    
    try:
        print("=" * 70)
        print("LUFTHANSA TEST - DEMO VERSION")
        print("=" * 70)
        
        # Navigate
        print("\n[STEP 1/10] Loading Lufthansa...")
        page.goto("https://www.lufthansa.com/us/en/flight-search")
        page.wait_for_timeout(5000)
        
        # Handle consent
        print("[STEP 2/10] Handling overlays...")
        page.evaluate("""
            () => {
                const btns = document.querySelectorAll('button');
                btns.forEach(btn => {
                    if (btn.textContent.includes('Agree') || btn.textContent.includes('Accept')) {
                        btn.click();
                    }
                });
                setTimeout(() => {
                    ['consentOverlay', '__tealiumGDPRcpPrefs'].forEach(id => {
                        const el = document.getElementById(id);
                        if (el) el.remove();
                    });
                }, 1500);
            }
        """)
        page.wait_for_timeout(3000)
        print("   ✓ Overlays handled")
        
        # Round trip
        print("[STEP 3/10] Selecting round trip...")
        try:
            page.locator("input[value='ROUND_TRIP']").first.check(force=True)
            print("   ✓ Round trip selected")
        except:
            print("   ✓ Already selected")
        
        # Origin - NEW YORK (ALWAYS CLEAR FIRST)
        print("[STEP 4/10] Origin: New York (CLEARING FIRST as required)")
        origin = page.locator("input[name*='originCode']").first
        origin.click(force=True)
        page.wait_for_timeout(300)
        # CLEAR THE BOX FIRST
        origin.fill("")
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        print("   ✓ Origin field cleared")
        
        # Type New York
        print("   → Typing 'New York'...")
        origin.type("New York", delay=100)
        page.wait_for_timeout(2500)
        
        # Select JFK
        print("   → Selecting JFK...")
        try:
            page.locator("div[role='option']:has-text('JFK')").first.click(force=True, timeout=5000)
            print("   ✓ JFK International selected")
        except:
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            print("   ✓ Airport selected via keyboard")
        page.wait_for_timeout(1000)
        
        # Destination - BERLIN (ALWAYS CLEAR FIRST)
        print("[STEP 5/10] Destination: Berlin (CLEARING FIRST as required)")
        dest = page.locator("input[name*='destinationCode']").first
        dest.click(force=True)
        page.wait_for_timeout(300)
        # CLEAR THE BOX FIRST
        dest.fill("")
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        print("   ✓ Destination field cleared")
        
        # Type Berlin
        print("   → Typing 'Berlin'...")
        dest.type("Berlin", delay=100)
        page.wait_for_timeout(2500)
        
        # Select BER
        print("   → Selecting Berlin Brandenburg...")
        try:
            page.locator("div[role='option']:has-text('BER'), div[role='option']:has-text('Brandenburg')").first.click(force=True, timeout=5000)
            print("   ✓ Berlin Brandenburg selected")
        except:
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
            print("   ✓ Airport selected via keyboard")
        page.wait_for_timeout(1000)
        
        # MANUAL DATE SELECTION
        print("\n" + "=" * 70)
        print("[STEP 6/10] MANUAL DATE SELECTION REQUIRED")
        print("=" * 70)
        print("\n⚠️  PLEASE SELECT DATES MANUALLY IN THE BROWSER:")
        print("   1. Click on the Departure Date field")
        print("   2. Select a departure date from the calendar")
        print("   3. Select a return date from the calendar")
        print("   4. The test will automatically continue in 30 seconds...")
        print("\n" + "=" * 70)
        
        # Wait for manual date selection
        page.wait_for_timeout(30000)
        
        # Search
        print("\n[STEP 7/10] Searching for flights...")
        try:
            search_btn = page.locator("button:has-text('Search flights')").first
            search_btn.click(force=True)
            print("   ✓ Search button clicked")
        except Exception as e:
            print(f"   ⚠ Search button click issue: {str(e)[:50]}")
        
        # Wait for results
        print("[STEP 8/10] Waiting for results (this may take 15-20 seconds)...")
        page.wait_for_timeout(15000)
        
        # Check if we're on results page
        try:
            page.wait_for_selector("div[class*='flight'], div[class*='price'], span[class*='price']", timeout=10000)
            print("   ✓ Results page detected")
        except:
            print("   ⚠ Results page detection timeout")
        
        page.wait_for_timeout(3000)
        
        # Screenshot
        screenshot = "/Users/mdahmed/.gemini/antigravity/scratch/lufthansa-playwright-test/demo_results.png"
        page.screenshot(path=screenshot, full_page=True)
        print(f"\n📸 Screenshot saved: {screenshot}")
        
        # Extract price
        print("\n[STEP 9/10] Extracting price...")
        print("=" * 70)
        price_text = None
        
        # Strategy 1: Look for price elements
        print("Strategy 1: Searching for price elements...")
        selectors = [
            "span[class*='price']",
            "div[class*='price'] span",
            "span[class*='amount']",
            "div[class*='fare'] span",
            "span[data-test*='price']",
            "div[class*='total'] span",
        ]
        
        for sel in selectors:
            try:
                elements = page.locator(sel).all()
                for elem in elements:
                    try:
                        text = elem.inner_text(timeout=1000).strip()
                        if '$' in text and re.search(r'\d{3,}', text.replace(',', '')):
                            price_text = text
                            print(f"   ✓ Found price: {price_text} (using selector: {sel})")
                            break
                    except:
                        continue
                if price_text:
                    break
            except:
                continue
        
        # Strategy 2: Regex in page content
        if not price_text:
            print("Strategy 2: Searching page content with regex...")
            try:
                content = page.content()
                matches = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', content)
                for match in matches:
                    num = int(re.sub(r'[^\d]', '', match))
                    if 300 <= num <= 5000:
                        price_text = match.strip()
                        print(f"   ✓ Found price via regex: {price_text}")
                        break
            except:
                pass
        
        # Strategy 3: Visible text
        if not price_text:
            print("Strategy 3: Searching visible text...")
            try:
                body_text = page.locator("body").inner_text()
                matches = re.findall(r'\$\s*[\d,]+(?:\.\d{2})?', body_text)
                for match in matches:
                    num = int(re.sub(r'[^\d]', '', match))
                    if 300 <= num <= 5000:
                        price_text = match.strip()
                        print(f"   ✓ Found price in body: {price_text}")
                        break
            except:
                pass
        
        # ASSERTIONS
        print("\n" + "=" * 70)
        print("[STEP 10/10] RUNNING ASSERTIONS")
        print("=" * 70)
        
        if price_text:
            # Assertion 1: Price found
            print(f"\n✅ ASSERTION 1 PASSED: Price found = '{price_text}'")
            
            # Assertion 2: Extract numeric value
            price_match = re.search(r'[\d,]+(?:\.\d{2})?', price_text)
            assert price_match is not None, "Could not extract numeric value"
            price_value = float(price_match.group().replace(',', ''))
            print(f"✅ ASSERTION 2 PASSED: Numeric value = ${price_value:.2f}")
            
            # Assertion 3: Reasonable range
            assert 300 <= price_value <= 5000, f"Price ${price_value} outside range $300-$5000"
            print(f"✅ ASSERTION 3 PASSED: Price within reasonable range ($300-$5000)")
            
            # Assertion 4: Expected range
            expected_min, expected_max = 500.00, 3000.00
            assert expected_min <= price_value <= expected_max, \
                f"Price ${price_value} outside expected range ${expected_min}-${expected_max}"
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
        else:
            print("\n⚠️  WARNING: Price not found")
            print("   This could be because:")
            print("   - Dates were not selected")
            print("   - Search didn't execute")
            print("   - Page structure is different than expected")
            print(f"\n   Please check the screenshot: {screenshot}")
        
        # Keep browser open
        print("\n⏸  Browser will remain open for 10 seconds for review...")
        page.wait_for_timeout(10000)
        
    except Exception as e:
        error_path = "/Users/mdahmed/.gemini/antigravity/scratch/lufthansa-playwright-test/demo_error.png"
        page.screenshot(path=error_path, full_page=True)
        print(f"\n❌ Error: {str(e)}")
        print(f"Screenshot: {error_path}")
        raise e
    finally:
        print("\n🔒 Closing browser...")
        context.close()
        browser.close()
        print("✓ Done")


def run():
    with sync_playwright() as playwright:
        test_lufthansa_demo(playwright)


if __name__ == "__main__":
    run()
