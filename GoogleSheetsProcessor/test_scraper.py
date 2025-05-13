#!/usr/bin/env python3
# Debug script for testing the Katom scraper

import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent
import time
import traceback

def test_scrape(model_number, prefix, debug=True):
    """Test the scraping functionality with debug info"""
    # Clean model number
    model_number = ''.join(e for e in model_number if e.isalnum()).upper()
    if model_number.endswith("HC"):
        model_number = model_number[:-2]
    
    url = f"https://www.katom.com/{prefix}-{model_number}.html"
    print(f"Testing URL: {url}")
    
    # Set up Selenium with more verbose options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Add a consistent user agent (sometimes better than random)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    options.add_argument(f'user-agent={user_agent}')
    
    # Add debugging preferences
    if debug:
        options.add_argument("--enable-logging")
        options.add_argument("--v=1")
    
    print("Starting Chrome WebDriver...")
    driver = None
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        print(f"Navigating to {url}")
        driver.get(url)
        
        # Debug page title and URL
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Check for 404 or error page
        if "404" in driver.title or "not found" in driver.title.lower():
            print("ERROR: 404 page detected - product not found")
            if driver:
                driver.quit()
            return None
        
        # Get title with debug info
        print("Looking for product title...")
        try:
            # Wait for title to appear with timeout
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-name.mb-0"))
            )
            
            title_element = driver.find_element(By.CSS_SELECTOR, "h1.product-name.mb-0")
            title = title_element.text.strip()
            print(f"Found title: {title}")
            
            # If we got here, the product was found - continue with more scraping
            
            # Get description
            print("Looking for description...")
            try:
                tab_content = driver.find_element(By.CLASS_NAME, "tab-content")
                paragraphs = tab_content.find_elements(By.TAG_NAME, "p")
                if paragraphs:
                    print(f"Found {len(paragraphs)} paragraphs in description")
                    print(f"First paragraph: {paragraphs[0].text[:100]}...")
                else:
                    print("No paragraphs found in tab-content")
            except NoSuchElementException:
                print("Tab content element not found - trying alternative selectors")
                # Try alternative selectors
                try:
                    desc_elems = driver.find_elements(By.CSS_SELECTOR, ".product-description, .description, [id*='description']")
                    if desc_elems:
                        print(f"Found alternative description element: {desc_elems[0].get_attribute('class')}")
                    else:
                        print("No alternative description elements found")
                except:
                    print("Error finding alternative description elements")
            
            # Try to find specifications table
            print("Looking for specifications table...")
            try:
                specs_tables = driver.find_elements(By.CSS_SELECTOR, "table.table.table-condensed.specs-table")
                if specs_tables:
                    print(f"Found specs table with class='table table-condensed specs-table'")
                    rows = specs_tables[0].find_elements(By.TAG_NAME, "tr")
                    print(f"Table has {len(rows)} rows")
                    # Print first few rows for debugging
                    for i, row in enumerate(rows[:3]):  # First 3 rows only
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 2:
                            print(f"  Row {i+1}: {cells[0].text} = {cells[1].text}")
                else:
                    print("No specs table found with primary selector, trying generic tables")
                    tables = driver.find_elements(By.TAG_NAME, "table")
                    if tables:
                        print(f"Found {len(tables)} generic tables")
                    else:
                        print("No tables found at all")
            except Exception as e:
                print(f"Error finding specs table: {e}")
            
            # Basic page structure analysis
            print("\nPage structure analysis:")
            try:
                all_headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")
                print(f"Found {len(all_headings)} headings on page")
                for i, h in enumerate(all_headings[:5]):  # First 5 headings
                    print(f"  Heading {i+1}: {h.tag_name} - {h.text[:50]}")
                
                # Look for common product page elements
                price_elems = driver.find_elements(By.CSS_SELECTOR, "[class*='price']")
                if price_elems:
                    print(f"Found price elements: {price_elems[0].text}")
                else:
                    print("No price elements found")
                
                # Look for product image
                img_elems = driver.find_elements(By.CSS_SELECTOR, "[class*='product'] img")
                if img_elems:
                    print(f"Found product image: {img_elems[0].get_attribute('src')}")
                else:
                    print("No product images found")
                
            except Exception as e:
                print(f"Error in page structure analysis: {e}")
            
            # Return success
            return {
                "title": title,
                "url": url,
                "success": True
            }
            
        except TimeoutException:
            print(f"ERROR: Timeout waiting for title element")
            # Save page source for debugging
            with open(f"debug_{model_number}.html", "w") as f:
                f.write(driver.page_source)
            print(f"Saved page source to debug_{model_number}.html")
            return None
            
        except Exception as e:
            print(f"ERROR getting title: {e}")
            print(traceback.format_exc())
            return None
            
    except Exception as e:
        print(f"ERROR in scrape process: {e}")
        print(traceback.format_exc())
        return None
        
    finally:
        # Ensure driver is closed
        if driver:
            print("Closing Chrome WebDriver")
            try:
                driver.quit()
            except:
                pass

# Test with a few models and prefixes
print("\n=== SCRAPER TEST SCRIPT ===\n")

# Test cases - adjust these to match your real data
test_cases = [
    {"model": "64900K", "prefix": "150"},  # Replace with a real model/prefix from your data
    {"model": "64901K", "prefix": "150"},  # Try another model
    # Add more test cases as needed
]

print(f"Running {len(test_cases)} test cases...\n")

for i, test in enumerate(test_cases):
    print(f"\n=== Test Case {i+1}: {test['model']} with prefix {test['prefix']} ===")
    result = test_scrape(test['model'], test['prefix'])
    if result:
        print(f"✅ SUCCESS: Found product {result['title']}")
    else:
        print(f"❌ FAILED: Could not scrape product data")
    print("-" * 50)
    # Add a delay between tests to prevent rate limiting
    if i < len(test_cases) - 1:
        print("Waiting 5 seconds before next test...")
        time.sleep(5)

print("\nScraper test completed. Check the output above for details.")
