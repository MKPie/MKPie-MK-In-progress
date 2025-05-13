#!/usr/bin/env python3
# debug_scraper.py - Enhanced scraper with debugging and fixes

import os
import re
import sys
import math
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from fake_useragent import UserAgent

def debug_scrape_katom(model_number, prefix, retries=2):
    """Enhanced version of scrape_katom with retry logic, better error handling, and debugging"""
    # Clean model number
    model_number = ''.join(e for e in model_number if e.isalnum()).upper()
    if model_number.endswith("HC"):
        model_number = model_number[:-2]
    
    url = f"https://www.katom.com/{prefix}-{model_number}.html"
    print(f"DEBUG SCRAPER: Scraping URL: {url}")
    
    # Use consistent user agent instead of random
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    
    # Empty return values
    title, description = "Title not found", "Description not found"
    specs_data = {}
    specs_html = ""
    video_links = ""
    main_image = ""
    additional_images = []
    
    # Implement retry logic
    for attempt in range(retries + 1):
        driver = None
        try:
            # Set up Selenium
            print(f"DEBUG SCRAPER: Setting up Chrome WebDriver (attempt {attempt+1}/{retries+1})...")
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'user-agent={user_agent}')
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)  # Set timeout to prevent hanging
            
            # Navigate to URL
            print(f"DEBUG SCRAPER: Navigating to URL: {url}")
            driver.get(url)
            
            # Check for 404
            if "404" in driver.title or "not found" in driver.title.lower():
                print(f"DEBUG SCRAPER: Product not found at {url}")
                if driver:
                    driver.quit()
                # No need to retry for 404, it's a definitive result
                return title, description, specs_data, specs_html, video_links, main_image, additional_images
            
            # Output title for debugging
            print(f"DEBUG SCRAPER: Page title: {driver.title}")
            
            # Get title
            found_title = False
            try:
                # Try multiple selectors for the title
                title_selectors = [
                    "h1.product-name.mb-0",
                    "h1.product-name",
                    "h1[class*='product-name']",
                    "h1[class*='title']",
                    ".product-title h1",
                    ".product-title",
                    "h1"
                ]
                
                # Try each selector
                for selector in title_selectors:
                    print(f"DEBUG SCRAPER: Trying title selector: {selector}")
                    title_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if title_elements:
                        title_element = title_elements[0]
                        title = title_element.text.strip()
                        if title:
                            found_title = True
                            print(f"DEBUG SCRAPER: Found title with selector {selector}: {title}")
                            break
                
                if not found_title:
                    print("DEBUG SCRAPER: Could not find title with any selector")
            except Exception as e:
                print(f"DEBUG SCRAPER: Error getting title: {e}")
                print(traceback.format_exc())
            
            # If we found a title, get the rest of the data
            if found_title:
                # Get description
                try:
                    print("DEBUG SCRAPER: Looking for description...")
                    desc_selectors = [
                        ".tab-content",
                        ".product-description",
                        "#product-description",
                        ".description",
                        "#description"
                    ]
                    
                    for selector in desc_selectors:
                        desc_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if desc_elements:
                            # Try to get paragraphs from the description element
                            paragraphs = desc_elements[0].find_elements(By.TAG_NAME, "p")
                            if paragraphs:
                                filtered = [
                                    f"<p>{p.text.strip()}</p>" for p in paragraphs
                                    if p.text.strip() and not p.text.lower().startswith("*free") and "video" not in p.text.lower()
                                ]
                                if filtered:
                                    description = "".join(filtered)
                                    print(f"DEBUG SCRAPER: Found description with {len(filtered)} paragraphs")
                                    break
                    
                    # If no description found, try to get the text content
                    if description == "Description not found":
                        for selector in desc_selectors:
                            desc_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if desc_elements:
                                text = desc_elements[0].text.strip()
                                if text:
                                    description = f"<p>{text}</p>"
                                    print(f"DEBUG SCRAPER: Found description text: {text[:50]}...")
                                    break
                except Exception as e:
                    print(f"DEBUG SCRAPER: Error getting description: {e}")
                    print(traceback.format_exc())
                
                # Extract table data and HTML
                try:
                    print("DEBUG SCRAPER: Looking for specifications table...")
                    specs_data, specs_html = extract_table_data(driver)
                    print(f"DEBUG SCRAPER: Found {len(specs_data)} specification entries")
                except Exception as e:
                    print(f"DEBUG SCRAPER: Error extracting table data: {e}")
                    print(traceback.format_exc())
                
                # Extract video links
                try:
                    print("DEBUG SCRAPER: Looking for video links...")
                    video_links = extract_video_links(driver)
                    if video_links:
                        print(f"DEBUG SCRAPER: Found video links: {video_links}")
                    else:
                        print("DEBUG SCRAPER: No video links found")
                except Exception as e:
                    print(f"DEBUG SCRAPER: Error extracting video links: {e}")
                    print(traceback.format_exc())
                
                # Extract images
                try:
                    print("DEBUG SCRAPER: Looking for images...")
                    from image_extractor import extract_images
                    main_image, additional_images = extract_images(driver)
                    if main_image:
                        print(f"DEBUG SCRAPER: Found main image: {main_image}")
                    else:
                        print("DEBUG SCRAPER: No main image found")
                        
                    if additional_images:
                        print(f"DEBUG SCRAPER: Found {len(additional_images)} additional images")
                    else:
                        print("DEBUG SCRAPER: No additional images found")
                except Exception as e:
                    print(f"DEBUG SCRAPER: Error extracting images: {e}")
                    print(traceback.format_exc())
                
                # Success! No need for more retries
                print(f"DEBUG SCRAPER: Successfully scraped {url}")
                break
                
            else:
                # Title not found, maybe retry
                if attempt < retries:
                    retry_wait = (attempt + 1) * 2  # Progressive backoff
                    print(f"DEBUG SCRAPER: Title not found. Retry {attempt+1}/{retries} in {retry_wait} seconds...")
                    time.sleep(retry_wait)
                else:
                    print(f"DEBUG SCRAPER: All retries failed for {url}")
            
        except Exception as e:
            print(f"DEBUG SCRAPER: Error in scrape attempt {attempt+1}: {e}")
            print(traceback.format_exc())
            
            # Only retry if this wasn't the last attempt
            if attempt < retries:
                retry_wait = (attempt + 1) * 2  # Progressive backoff
                print(f"DEBUG SCRAPER: Retry {attempt+1}/{retries} in {retry_wait} seconds...")
                time.sleep(retry_wait)
        
        finally:
            # Ensure driver is always closed, even if an exception occurs
            if driver:
                try:
                    driver.quit()
                    print("DEBUG SCRAPER: WebDriver closed")
                except:
                    print("DEBUG SCRAPER: Error closing WebDriver")
    
    # Print summary of what we found
    print("\nDEBUG SCRAPER RESULTS SUMMARY:")
    print(f"Title: {title}")
    print(f"Description: {description[:100]}..." if len(description) > 100 else f"Description: {description}")
    print(f"Specs data entries: {len(specs_data)}")
    print(f"Specs HTML length: {len(specs_html)}")
    print(f"Video links: {video_links or 'None'}")
    print(f"Main image: {main_image or 'None'}")
    print(f"Additional images: {len(additional_images)}")
    
    return title, description, specs_data, specs_html, video_links, main_image, additional_images

def extract_table_data(driver):
    """
    Extract table data both as a dictionary of key-value pairs AND as an HTML table.
    Returns a tuple: (specs_dict, specs_html)
    """
    specs_dict = {}
    specs_html = ""
    
    try:
        # Try multiple approaches to find the table
        
        # First, try to get the original table HTML
        specs_tables = driver.find_elements(By.CSS_SELECTOR, "table.table.table-condensed.specs-table")
        
        if not specs_tables:
            # Try generic tables
            specs_tables = driver.find_elements(By.TAG_NAME, "table")
        
        if specs_tables:
            # Extract key-value pairs from the table
            table = specs_tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # Build a clean table with slim styling
            specs_html = '<table class="specs-table" cellspacing="0" cellpadding="4" border="1" style="margin-top:10px;border-collapse:collapse;width:auto;" align="left"><tbody>'
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    
                    # Check if this is a weight field and process accordingly
                    if "weight" in key.lower():
                        value = process_weight_value(value)
                    
                    # Add to the dictionary
                    if key and not key.lower() in specs_dict:
                        specs_dict[key.lower()] = value
                    
                    # Add to the HTML table
                    specs_html += f'<tr><td style="padding:3px 8px;"><b>{key}</b></td><td style="padding:3px 8px;">{value}</td></tr>'
            
            specs_html += "</tbody></table>"
        
        # If no table found or no HTML extracted, create an HTML table from the data we find
        if not specs_html or specs_html == "":
            # Start building an HTML table
            other_specs = []
            
            # Try to find spec elements in various ways
            
            # Method 1: Look for dedicated spec elements
            spec_rows = driver.find_elements(By.CSS_SELECTOR, ".specs-row, [class*='spec']")
            if spec_rows:
                for row in spec_rows:
                    key_elem = row.find_elements(By.CSS_SELECTOR, ".spec-key, .spec-name, [class*='key'], [class*='name']")
                    val_elem = row.find_elements(By.CSS_SELECTOR, ".spec-value, .spec-val, [class*='value'], [class*='val']")
                    
                    if key_elem and val_elem:
                        key = key_elem[0].text.strip()
                        value = val_elem[0].text.strip()
                        
                        # Check if this is a weight field and process accordingly
                        if "weight" in key.lower():
                            value = process_weight_value(value)
                            
                        if key:
                            other_specs.append((key, value))
                            if not key.lower() in specs_dict:
                                specs_dict[key.lower()] = value
            
            # Method 2: Look for definition lists
            if not other_specs:
                dl_elements = driver.find_elements(By.TAG_NAME, "dl")
                for dl in dl_elements:
                    terms = dl.find_elements(By.TAG_NAME, "dt")
                    definitions = dl.find_elements(By.TAG_NAME, "dd")
                    
                    for i in range(min(len(terms), len(definitions))):
                        key = terms[i].text.strip()
                        value = definitions[i].text.strip()
                        
                        # Check if this is a weight field and process accordingly
                        if "weight" in key.lower():
                            value = process_weight_value(value)
                            
                        if key:
                            other_specs.append((key, value))
                            if not key.lower() in specs_dict:
                                specs_dict[key.lower()] = value
            
            # Method 3: Look for text patterns in all content
            if not other_specs:
                # Get all elements that might contain specs
                elements = driver.find_elements(By.CSS_SELECTOR, "p, div, li, span")
                
                # Common spec terms to look for - expand this list as needed
                common_specs = [
                    "manufacturer", "food type", "frypot style", "heat", "hertz", "nema", 
                    "number of", "oil capacity", "phase", "product", "type", "rating", 
                    "special features", "voltage", "warranty", "weight", "dimensions"
                ]
                
                for element in elements:
                    text = element.text.strip()
                    if not text or len(text) > 100:  # Skip empty or very long text
                        continue
                    
                    # Look for patterns like "Key: Value" or "Key - Value"
                    for pattern in [r'([^:]+):\s*(.+)', r'([^-]+)-\s*(.+)']: 
                        match = re.match(pattern, text)
                        if match:
                            key = match.group(1).strip()
                            value = match.group(2).strip()
                            
                            # Check if this is a weight field and process accordingly
                            if "weight" in key.lower():
                                value = process_weight_value(value)
                            
                            # Check if this key is one of our common specs
                            if any(spec in key.lower() for spec in common_specs):
                                other_specs.append((key, value))
                                if not key.lower() in specs_dict:
                                    specs_dict[key.lower()] = value
                                break
            
            # Create HTML table from the data we collected
            if other_specs:
                specs_html = '<table class="specs-table" cellspacing="0" cellpadding="4" border="1" style="margin-top:10px;border-collapse:collapse;width:auto;" align="left"><tbody>'
                for key, value in other_specs:
                    specs_html += f'<tr><td style="padding:3px 8px;"><b>{key}</b></td><td style="padding:3px 8px;">{value}</td></tr>'
                specs_html += "</tbody></table>"
    
    except Exception as e:
        print(f"Error extracting table data: {e}")
        print(traceback.format_exc())
    
    return specs_dict, specs_html

def extract_video_links(driver):
    """Extract video links from the page"""
    video_links = ""
    
    try:
        # Find source tags with .mp4 files
        sources = driver.find_elements(By.CSS_SELECTOR, "source[src*='.mp4'], source[type*='video']")
        for source in sources:
            src = source.get_attribute("src")
            if src and src not in video_links:
                video_links += f"{src}\n"
        
        # If no video sources found, look for video elements
        if not video_links:
            videos = driver.find_elements(By.TAG_NAME, "video")
            for video in videos:
                # Try to get source elements within video tag
                inner_sources = video.find_elements(By.TAG_NAME, "source")
                for source in inner_sources:
                    src = source.get_attribute("src")
                    if src and src not in video_links:
                        video_links += f"{src}\n"
                        
        # Last resort - extract video URLs from the page source
        if not video_links:
            page_source = driver.page_source
            # Look for .mp4 URLs in the source
            mp4_pattern = r'https?://[^"\']+\.mp4'
            matches = re.findall(mp4_pattern, page_source)
            for match in matches:
                if match not in video_links:
                    video_links += f"{match}\n"
    except Exception as e:
        print(f"Error extracting video links: {e}")
        print(traceback.format_exc())
    
    return video_links

def process_weight_value(value):
    """Process weight values: round up to whole number and add 5"""
    try:
        # Try to extract a number from the string
        # This handles cases like "22.93" or "22.93 lbs"
        number_match = re.search(r'(\d+(\.\d+)?)', str(value))
        if number_match:
            # Extract the number
            number = float(number_match.group(1))
            
            # Round up to nearest whole number
            rounded = math.ceil(number)
            
            # Add 5
            final = rounded + 5
            
            # If the original had units, keep them
            units_match = re.search(r'[^\d.]+$', str(value))
            units = units_match.group(0).strip() if units_match else ""
            
            return f"{final}{' ' + units if units else ''}"
        return value
    except:
        # If any error occurs, return the original value
        return value

if __name__ == "__main__":
    print("This script is meant to be imported into main.py")
    print("Example usage:")
    print("from debug_scraper import debug_scrape_katom")
    print("title, description, specs_data, specs_html, video_links, main_image, additional_images = debug_scrape_katom(model_number, prefix)")
