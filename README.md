# Lufthansa Flight Booking Test - Playwright Python

This project contains a Playwright automation test for the Lufthansa flight booking system, specifically testing a round-trip flight search from New York (JFK) to Berlin (BER).

## Features

- ✅ Automated flight search on Lufthansa.com
- ✅ Clears input fields before typing (as per requirement)
- ✅ Handles cookie consent and feedback forms
- ✅ Selects round-trip flights from New York to Berlin
- ✅ Extracts and validates flight prices
- ✅ Multiple fallback strategies for price extraction
- ✅ Screenshots on success and error
- ✅ Comprehensive error handling

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

## Usage

### Run the test directly:
```bash
python test_lufthansa_booking.py
```

### Run with pytest:
```bash
pytest test_lufthansa_booking.py -v -s
```

## Test Details

### Test Flow:
1. Navigate to Lufthansa homepage
2. Accept cookie consent (if present)
3. Close feedback forms (if present)
4. Navigate to flight search page
5. Select round-trip option
6. **Clear and fill** origin field: "New York"
7. Select JFK International Airport
8. **Clear and fill** destination field: "Berlin"
9. Select Berlin Brandenburg Airport
10. Select departure and return dates
11. Click "Search flights"
12. Wait for results to load
13. Extract price information
14. Assert price is valid and within expected range

### Price Assertions:
- Price must be found on the page
- Price must be in valid format (contains $ and numbers)
- Price must be between $300 and $5000 (sanity check)
- Price must be between $500 and $3000 (expected range for this route)

### Screenshots:
- Success: `search_results.png`
- Error: `error_screenshot.png`

## Customization

You can modify the expected price range in the test:

```python
expected_price_min = 500.00
expected_price_max = 3000.00
```

You can also change the dates or other search parameters in the script.

## Notes

- The script runs in **non-headless mode** (`headless=False`) so you can see the browser actions
- There's a `slow_mo=500` parameter to slow down actions for better visibility
- The script includes multiple fallback strategies for finding prices due to dynamic page structure
- All input fields are cleared before typing, as per requirements

## Troubleshooting

If the test fails:
1. Check the error screenshot in the project directory
2. Ensure you have a stable internet connection
3. The Lufthansa website structure may have changed - update selectors if needed
4. Dates might need adjustment if they're in the past

## License

This is a test automation script for educational purposes.
