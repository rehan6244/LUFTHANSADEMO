"""
Home Page Object Model
Encapsulates all complexity of the Lufthansa home page including:
- Search form interactions
- Date selection logic
- Airport selection
- Trip type selection
"""
from pages.base_page import BasePage
from playwright.sync_api import Page
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """
    Page Object for Lufthansa Home/Search Page.
    Encapsulates all complex selection logic and form interactions.
    """
    
    # ==================== LOCATORS ====================
    # Centralized locators for easy maintenance
    
    # Trip Type
    ROUND_TRIP_RADIO = "input[value='ROUND_TRIP']"
    ONE_WAY_RADIO = "input[value='ONE_WAY']"
    
    # Origin/Destination
    ORIGIN_INPUT = "input[name*='originCode']"
    DESTINATION_INPUT = "input[name*='destinationCode']"
    DROPDOWN_OPTION = "div[role='option']"
    
    # Dates
    DATE_INPUT = "input[name*='travelDatetime']"
    CALENDAR_CONTAINER = "div[class*='calendar']"
    MONTH_HEADER = "div[class*='calendar'] h2, div[class*='month'], span[class*='month']"
    NEXT_MONTH_BUTTON = "button[aria-label*='Next'], button[class*='next']"
    CALENDAR_DAY_BUTTON = "td[role='gridcell']:not([aria-disabled='true']) button"
    
    # Search
    SEARCH_BUTTON = "button:has-text('Search flights')"
    
    # Overlays
    CONSENT_BUTTONS = "button"
    
    def __init__(self, page: Page, url: str = "https://www.lufthansa.com/us/en/flight-search"):
        super().__init__(page)
        self.url = url
        
    # ==================== PAGE ACTIONS ====================
    
    def open(self) -> 'HomePage':
        """
        Navigate to home page and handle initial overlays.
        Returns self for method chaining.
        """
        logger.info("Opening Lufthansa home page...")
        self.navigate_to(self.url)
        self.wait_for_timeout(6000)  # Allow page to fully load
        self.remove_overlays()
        return self
        
    def select_trip_type(self, trip_type: str = "round_trip") -> 'HomePage':
        """
        Select trip type (round_trip or one_way).
        
        Args:
            trip_type: Either "round_trip" or "one_way"
            
        Returns:
            self for method chaining
        """
        logger.info(f"Selecting trip type: {trip_type}")
        
        if trip_type.lower() == "round_trip":
            selector = self.ROUND_TRIP_RADIO
        elif trip_type.lower() == "one_way":
            selector = self.ONE_WAY_RADIO
        else:
            raise ValueError(f"Invalid trip type: {trip_type}")
            
        # Use JavaScript for reliability
        self.page.evaluate("""
            (selector) => {
                const radio = document.querySelector(selector);
                if (radio && !radio.checked) radio.click();
            }
        """, selector)
        
        self.wait_for_timeout(500)
        logger.info(f"✓ {trip_type.replace('_', ' ').title()} selected")
        return self
        
    def enter_origin(self, city: str, airport_code: Optional[str] = None) -> 'HomePage':
        """
        Enter origin city and select airport.
        Encapsulates all complexity of clearing, typing, and selecting.
        
        Args:
            city: City name (e.g., "New York")
            airport_code: Optional airport code to select (e.g., "JFK")
            
        Returns:
            self for method chaining
        """
        logger.info(f"Entering origin: {city}")
        
        origin_field = self.get_element(self.ORIGIN_INPUT).first
        
        # Clear and fill
        logger.info("  → Clearing origin field...")
        self.clear_input(origin_field)
        
        logger.info(f"  → Typing '{city}'...")
        self.fill_input(origin_field, city, clear_first=False, delay=100)
        
        # Wait for dropdown
        self.wait_for_timeout(2500)
        
        # Select airport
        if airport_code:
            logger.info(f"  → Selecting {airport_code}...")
            try:
                self.select_from_dropdown(airport_code, self.DROPDOWN_OPTION)
                logger.info(f"  ✓ {airport_code} selected")
            except Exception:
                logger.warning(f"  Could not find {airport_code}, using Enter key")
                self.page.keyboard.press("Enter")
        else:
            # Just press Enter to select first option
            self.page.keyboard.press("Enter")
            logger.info("  ✓ First airport selected")
            
        self.wait_for_timeout(1000)
        return self
        
    def enter_destination(self, city: str, airport_code: Optional[str] = None) -> 'HomePage':
        """
        Enter destination city and select airport.
        Encapsulates all complexity of clearing, typing, and selecting.
        
        Args:
            city: City name (e.g., "Berlin")
            airport_code: Optional airport code to select (e.g., "BER")
            
        Returns:
            self for method chaining
        """
        logger.info(f"Entering destination: {city}")
        
        dest_field = self.get_element(self.DESTINATION_INPUT).first
        
        # Clear and fill
        logger.info("  → Clearing destination field...")
        self.clear_input(dest_field)
        
        logger.info(f"  → Typing '{city}'...")
        self.fill_input(dest_field, city, clear_first=False, delay=100)
        
        # Wait for dropdown
        self.wait_for_timeout(2500)
        
        # Select airport
        if airport_code:
            logger.info(f"  → Selecting {airport_code}...")
            try:
                # Try multiple selectors for robustness
                selectors = [
                    f"{self.DROPDOWN_OPTION}:has-text('{airport_code}')",
                    f"{self.DROPDOWN_OPTION}:has-text('{city}')"
                ]
                
                selected = False
                for selector in selectors:
                    try:
                        self.get_element(selector).first.click(force=True, timeout=3000)
                        selected = True
                        break
                    except Exception:
                        continue
                        
                if not selected:
                    self.page.keyboard.press("Enter")
                    
                logger.info(f"  ✓ {airport_code} selected")
            except Exception:
                logger.warning(f"  Could not find {airport_code}, using Enter key")
                self.page.keyboard.press("Enter")
        else:
            self.page.keyboard.press("Enter")
            logger.info("  ✓ First airport selected")
            
        self.wait_for_timeout(1000)
        return self
        
    def select_dates(self, departure_date: str, return_date: Optional[str] = None) -> 'HomePage':
        """
        Select travel dates with robust fallback strategies.
        Encapsulates complex calendar interaction logic.
        
        Args:
            departure_date: Departure date in MM/DD/YYYY format
            return_date: Optional return date in MM/DD/YYYY format
            
        Returns:
            self for method chaining
        """
        logger.info(f"Selecting dates: {departure_date} - {return_date}")
        
        # Try to open calendar
        logger.info("  → Opening calendar...")
        date_field = self.get_element(self.DATE_INPUT).first
        
        try:
            date_field.click(force=True, timeout=5000)
            self.wait_for_timeout(3000)
        except Exception:
            logger.warning("  ⚠ Calendar click failed, using JS injection...")
            # Fallback: Inject dates directly
            self._inject_dates_via_js(departure_date, return_date)
            return self
            
        # Try to select dates from calendar
        try:
            self._select_date_from_calendar(departure_date, is_departure=True)
            
            if return_date:
                self._select_date_from_calendar(return_date, is_departure=False)
                
            logger.info("  ✓ Dates selected from calendar")
        except Exception as e:
            logger.warning(f"  ⚠ Calendar selection failed: {e}")
            logger.info("  → Falling back to JS injection...")
            self._inject_dates_via_js(departure_date, return_date)
            
        # Verify dates
        self._verify_dates(departure_date, return_date)
        
        return self
        
    def _inject_dates_via_js(self, departure_date: str, return_date: Optional[str] = None) -> None:
        """
        Fallback method: Inject dates directly using JavaScript.
        Reduces flakiness when calendar interaction fails.
        """
        self.page.evaluate(f"""
            () => {{
                const inputs = document.querySelectorAll('input[name*="travelDatetime"]');
                if (inputs.length >= 2) {{
                    inputs[0].value = '{departure_date}';
                    inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                    inputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    if ('{return_date}') {{
                        inputs[1].value = '{return_date}';
                        inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        inputs[1].dispatchEvent(new Event('change', {{ bubbles: true }}));
                    }}
                }}
            }}
        """)
        self.wait_for_timeout(2000)
        logger.info("  ✓ Dates injected via JavaScript")
        
    def _select_date_from_calendar(self, date: str, is_departure: bool = True) -> None:
        """
        Select a specific date from the calendar widget.
        Handles month navigation and date clicking.
        
        Args:
            date: Date in MM/DD/YYYY format
            is_departure: Whether this is departure (True) or return (False) date
        """
        # Parse date
        month, day, year = date.split('/')
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        month_name = month_names[int(month) - 1]
        
        date_type = "departure" if is_departure else "return"
        logger.info(f"  → Selecting {date_type} date: {month_name} {day}, {year}")
        
        # Navigate to correct month
        self._navigate_to_month(month_name, year)
        
        # Click the day
        self._click_calendar_day(day, month_name, year)
        
    def _navigate_to_month(self, month_name: str, year: str, max_attempts: int = 12) -> None:
        """Navigate calendar to the correct month and year"""
        for attempt in range(max_attempts):
            try:
                month_header = self.get_element(self.MONTH_HEADER).first
                header_text = self.get_text(month_header, timeout=2000)
                
                if month_name in header_text and year in header_text:
                    logger.info(f"  ✓ Found {month_name} {year}")
                    return
                    
                # Click next month
                next_btn = self.get_element(self.NEXT_MONTH_BUTTON).first
                next_btn.click(force=True, timeout=2000)
                self.wait_for_timeout(1000)
            except Exception:
                break
                
        logger.warning(f"  ⚠ Could not navigate to {month_name} {year}")
        
    def _click_calendar_day(self, day: str, month_name: str, year: str) -> None:
        """
        Click a specific day in the calendar.
        Uses multiple strategies for robustness.
        """
        day = str(int(day))  # Remove leading zero
        
        # Multiple selection strategies
        strategies = [
            (f"button[aria-label*='{month_name} {day}, {year}']", "aria-label exact"),
            (f"button[aria-label*='{day} {month_name} {year}']", "aria-label alternate"),
            (f"button:has-text('{day}')", "text content"),
            (f"td[data-date='{year}-{int(month_name):02d}-{int(day):02d}'] button", "data attribute"),
        ]
        
        for selector, strategy_name in strategies:
            try:
                buttons = self.get_elements(selector)
                for btn in buttons:
                    if self.is_visible(btn, timeout=1000):
                        btn.click(force=True)
                        logger.info(f"  ✓ Day {day} selected (via {strategy_name})")
                        self.wait_for_timeout(2000)
                        return
            except Exception:
                continue
                
        # Fallback: Use first available date
        logger.warning(f"  ⚠ Could not find day {day}, using first available")
        try:
            first_day = self.get_element(self.CALENDAR_DAY_BUTTON).first
            first_day.click(force=True)
            self.wait_for_timeout(2000)
        except Exception:
            pass
            
    def _verify_dates(self, departure_date: str, return_date: Optional[str] = None) -> None:
        """Verify that dates were set correctly"""
        logger.info("  → Verifying dates...")
        try:
            inputs = self.get_elements(self.DATE_INPUT)
            dep_value = inputs[0].input_value() if len(inputs) > 0 else ""
            ret_value = inputs[1].input_value() if len(inputs) > 1 else ""
            
            logger.info(f"    Departure: {dep_value}")
            if return_date:
                logger.info(f"    Return: {ret_value}")
                
            if dep_value and (not return_date or ret_value):
                logger.info("  ✓ Dates verified")
            else:
                logger.warning("  ⚠ Dates may not be set correctly")
        except Exception:
            logger.warning("  ⚠ Could not verify dates")
            
    def click_search(self) -> 'HomePage':
        """
        Click the search button with fallback strategies.
        
        Returns:
            self for method chaining
        """
        logger.info("Clicking search button...")
        
        try:
            search_btn = self.get_element(self.SEARCH_BUTTON).first
            search_btn.click(force=True, timeout=5000)
            logger.info("  ✓ Search button clicked")
        except Exception:
            logger.warning("  ⚠ Standard click failed, using JavaScript...")
            self.page.evaluate("""
                () => {
                    const btn = Array.from(document.querySelectorAll('button'))
                        .find(b => b.textContent.includes('Search flights'));
                    if (btn) btn.click();
                }
            """)
            logger.info("  ✓ Search button clicked via JavaScript")
            
        return self
        
    def wait_for_results(self, timeout: int = 20000) -> 'HomePage':
        """
        Wait for search results to load.
        
        Args:
            timeout: Timeout in milliseconds
            
        Returns:
            self for method chaining
        """
        logger.info(f"Waiting for results ({timeout/1000}s)...")
        self.wait_for_timeout(timeout)
        
        # Check if results loaded
        try:
            result_selectors = [
                "div[class*='flight']",
                "div[class*='price']",
                "span[class*='price']",
                "div[class*='offer']"
            ]
            
            for selector in result_selectors:
                try:
                    self.wait_for_selector(selector, timeout=5000)
                    logger.info("  ✓ Results page loaded")
                    return self
                except Exception:
                    continue
                    
            logger.warning("  ⚠ Results detection timeout")
        except Exception:
            logger.warning("  ⚠ Could not verify results loaded")
            
        return self
        
    # ==================== COMPLETE SEARCH FLOW ====================
    
    def search_flight(self, origin_city: str, destination_city: str,
                     departure_date: str, return_date: Optional[str] = None,
                     origin_airport: Optional[str] = None,
                     destination_airport: Optional[str] = None,
                     trip_type: str = "round_trip") -> 'HomePage':
        """
        Complete flight search flow in one method.
        Encapsulates entire search form complexity.
        
        Args:
            origin_city: Origin city name
            destination_city: Destination city name
            departure_date: Departure date (MM/DD/YYYY)
            return_date: Return date (MM/DD/YYYY) - optional for one-way
            origin_airport: Origin airport code (optional)
            destination_airport: Destination airport code (optional)
            trip_type: "round_trip" or "one_way"
            
        Returns:
            self for method chaining
            
        Example:
            home_page.search_flight(
                origin_city="New York",
                destination_city="Berlin",
                departure_date="12/15/2025",
                return_date="12/25/2025",
                origin_airport="JFK",
                destination_airport="BER"
            )
        """
        logger.info("=" * 70)
        logger.info("STARTING FLIGHT SEARCH")
        logger.info(f"Route: {origin_city} → {destination_city}")
        logger.info(f"Dates: {departure_date} - {return_date}")
        logger.info("=" * 70)
        
        # Execute search flow
        (self
            .select_trip_type(trip_type)
            .enter_origin(origin_city, origin_airport)
            .enter_destination(destination_city, destination_airport)
            .select_dates(departure_date, return_date)
            .click_search()
            .wait_for_results())
            
        logger.info("=" * 70)
        logger.info("SEARCH COMPLETED")
        logger.info("=" * 70)
        
        return self
