"""
This module contains patches for the Google Sheets Processor application.
It has been restructured to avoid circular imports with main.py.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import traceback
import pandas as pd
import os
import time
import re
import math

# Import decorator from local module
try:
    from decorators import retry_on_failure
except ImportError:
    # Define a fallback decorator if the module is not available
    def retry_on_failure(max_attempts=3, delay=2):
        def decorator(func):
            def wrapper(*args, **kwargs):
                attempts = 0
                while attempts < max_attempts:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        attempts += 1
                        if attempts >= max_attempts:
                            raise
                        print(f"Attempt {attempts} failed, retrying in {delay} seconds...")
                        time.sleep(delay)
            return wrapper
        return decorator

# The extract_table_data function - required by scrape_katom
def extract_table_data(self, driver):
    specs_dict = {}
    specs_html = ""
    try:
        specs_tables = driver.find_elements(By.CSS_SELECTOR, "table.table.table-condensed.specs-table")
        if not specs_tables:
            specs_tables = driver.find_elements(By.TAG_NAME, "table")
        if specs_tables:
            table = specs_tables[0]
            rows = table.find_elements(By.TAG_NAME, "tr")
            specs_html = '<table class="specs-table" cellspacing="0" cellpadding="4" border="1" style="margin-top:10px;border-collapse:collapse;width:auto;" align="left"><tbody>'
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    if "weight" in key.lower():
                        value = self.process_weight_value(value)
                    if key and key.lower() not in specs_dict:
                        specs_dict[key.lower()] = value
                    specs_html += f'<tr><td style="padding:3px 8px;"><b>{key}</b></td><td style="padding:3px 8px;">{value}</td></tr>'
            specs_html += "</tbody></table>"
        if not specs_html:
            other_specs = []
            spec_rows = driver.find_elements(By.CSS_SELECTOR, ".specs-row, [class*='spec']")
            if spec_rows:
                for row in spec_rows:
                    key_elem = row.find_elements(By.CSS_SELECTOR, ".spec-key, .spec-name, [class*='key'], [class*='name']")
                    val_elem = row.find_elements(By.CSS_SELECTOR, ".spec-value, .spec-val, [class*='value'], [class*='val']")
                    if key_elem and val_elem:
                        key = key_elem[0].text.strip()
                        value = val_elem[0].text.strip()
                        if "weight" in key.lower():
                            value = self.process_weight_value(value)
                        if key:
                            other_specs.append((key, value))
                            if key.lower() not in specs_dict:
                                specs_dict[key.lower()] = value
            if not other_specs:
                dl_elements = driver.find_elements(By.TAG_NAME, "dl")
                for dl in dl_elements:
                    terms = dl.find_elements(By.TAG_NAME, "dt")
                    definitions = dl.find_elements(By.TAG_NAME, "dd")
                    for i in range(min(len(terms), len(definitions))):
                        key = terms[i].text.strip()
                        value = definitions[i].text.strip()
                        if "weight" in key.lower():
                            value = self.process_weight_value(value)
                        if key:
                            other_specs.append((key, value))
                            if key.lower() not in specs_dict:
                                specs_dict[key.lower()] = value
            if not other_specs:
                elements = driver.find_elements(By.CSS_SELECTOR, "p, div, li, span")
                common_specs = [
                    "manufacturer", "food type", "frypot style", "heat", "hertz", "nema", 
                    "number of", "oil capacity", "phase", "product", "type", "rating", 
                    "special features", "voltage", "warranty", "weight", "dimensions"
                ]
                for element in elements:
                    text = element.text.strip()
                    if not text or len(text) > 100:
                        continue
                    for pattern in [r'([^:]+):\s*(.+)', r'([^-]+)-\s*(.+)']: 
                        match = re.match(pattern, text)
                        if match:
                            key = match.group(1).strip()
                            value = match.group(2).strip()
                            if "weight" in key.lower():
                                value = self.process_weight_value(value)
                            if any(spec in key.lower() for spec in common_specs):
                                other_specs.append((key, value))
                                if key.lower() not in specs_dict:
                                    specs_dict[key.lower()] = value
                                break
            if other_specs:
                specs_html = '<table class="specs-table" cellspacing="0" cellpadding="4" border="1" style="margin-top:10px;border-collapse:collapse;width:auto;" align="left"><tbody>'
                for key, value in other_specs:
                    specs_html += f'<tr><td style="padding:3px 8px;"><b>{key}</b></td><td style="padding:3px 8px;">{value}</td></tr>'
                specs_html += "</tbody></table>"
    except Exception as e:
        print(f"Error extracting table data: {e}")
    return specs_dict, specs_html

# The process_weight_value function - required by scrape_katom
def process_weight_value(self, value):
    try:
        number_match = re.search(r'(\d+(\.\d+)?)', str(value))
        if number_match:
            number = float(number_match.group(1))
            rounded = math.ceil(number)
            final = rounded + 5
            units_match = re.search(r'[^\d.]+$', str(value))
            units = units_match.group(0).strip() if units_match else ""
            return f"{final}{' ' + units if units else ''}"
        return value
    except:
        return value

def patched_scrape_katom(self, model_number, prefix, retries=2):
    """Patched version of the scrape_katom function that matches the original's return format"""
    model_number = ''.join(e for e in model_number if e.isalnum()).upper()
    if model_number.endswith("HC"):
        model_number = model_number[:-2]
    url = f"https://www.katom.com/{prefix}-{model_number}.html"
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Try to import fake_useragent and use it if available
    try:
        from fake_useragent import UserAgent
        options.add_argument(f'user-agent={UserAgent().random}')
    except ImportError:
        print("UserAgent not available, using default user agent")
    
    driver = None
    title, description = "Title not found", "Description not found"
    specs_data = {}
    specs_html = ""
    video_links = ""
    price = ""
    main_image = ""
    additional_images = []
    item_found = False
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.get(url)
        
        if "404" in driver.title or "not found" in driver.title.lower():
            return title, description, specs_data, specs_html, video_links, price, main_image, additional_images
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.product-name.mb-0"))
            )
            title_element = driver.find_element(By.CSS_SELECTOR, "h1.product-name.mb-0")
            title = title_element.text.strip()
            if title:
                item_found = True
        except TimeoutException:
            print(f"Timeout waiting for title element on {url}")
        except Exception as e:
            print(f"Error getting title: {e}")
            
        if item_found:
            # Try to get the price
            try:
                price_element = driver.find_element(By.CSS_SELECTOR, ".product-price, .price, [class*='price'], .regular-price")
                price = price_element.text.strip()
                if '$' not in price:
                    price = f"${price}"
            except NoSuchElementException:
                try:
                    price_element = driver.find_element(By.XPATH, "//*[contains(text(), '$')]")
                    price = price_element.text.strip()
                except:
                    price = ""
            except Exception as e:
                print(f"Error getting price: {e}")
                price = ""
                
            # Try to get the main product image
            try:
                main_image_element = driver.find_element(By.CSS_SELECTOR, ".product-img, .main-product-image, img.main-image, img[itemprop='image']")
                main_image = main_image_element.get_attribute("src")
            except NoSuchElementException:
                try:
                    img_elements = driver.find_elements(By.TAG_NAME, "img")
                    for img in img_elements:
                        src = img.get_attribute("src")
                        if model_number.lower() in src.lower() or "product" in src.lower():
                            main_image = src
                            break
                except:
                    main_image = ""
            except Exception as e:
                print(f"Error getting main image: {e}")
                main_image = ""
                
            # Try to get additional product images
            try:
                additional_image_elements = driver.find_elements(By.CSS_SELECTOR, ".additional-images img, .product-thumbnails img, .thumb-image")
                for img in additional_image_elements[:5]:  # Limit to 5 additional images
                    src = img.get_attribute("src")
                    if src and src != main_image:
                        additional_images.append(src)
            except Exception as e:
                print(f"Error getting additional images: {e}")
                
            # Get the description
            try:
                tab_content = driver.find_element(By.CLASS_NAME, "tab-content")
                paragraphs = tab_content.find_elements(By.TAG_NAME, "p")
                filtered = [
                    f"<p>{p.text.strip()}</p>" for p in paragraphs
                    if p.text.strip() and not p.text.lower().startswith("*free") and "video" not in p.text.lower()
                ]
                description = "".join(filtered) if filtered else "Description not found"
            except NoSuchElementException:
                print(f"Tab content not found on {url}")
                try:
                    desc_elements = driver.find_elements(By.CSS_SELECTOR, ".product-description, .description, [class*='description']")
                    if desc_elements:
                        description = desc_elements[0].text.strip()
                        description = f"<p>{description}</p>"
                except:
                    description = "Description not found"
            except Exception as e:
                print(f"Error getting description: {e}")
                
            # Extract table data
            if hasattr(self, 'extract_table_data'):
                specs_data, specs_html = self.extract_table_data(driver)
            else:
                specs_data, specs_html = extract_table_data(self, driver)
            
            # Extract video links
            try:
                sources = driver.find_elements(By.CSS_SELECTOR, "source[src*='.mp4'], source[type*='video']")
                for source in sources:
                    src = source.get_attribute("src")
                    if src and src not in video_links:
                        video_links += f"{src}\n"
                        
                if not video_links:
                    videos = driver.find_elements(By.TAG_NAME, "video")
                    for video in videos:
                        inner_sources = video.find_elements(By.TAG_NAME, "source")
                        for source in inner_sources:
                            src = source.get_attribute("src")
                            if src and src not in video_links:
                                video_links += f"{src}\n"
                                
                if not video_links:
                    page_source = driver.page_source
                    mp4_pattern = r'https?://[^"\']+\.mp4'
                    matches = re.findall(mp4_pattern, page_source)
                    for match in matches:
                        if match not in video_links:
                            video_links += f"{match}\n"
            except Exception as e:
                print(f"Error extracting video links: {e}")
                
    except Exception as e:
        print(f"Error in scrape_katom: {e}")
        print(traceback.format_exc())
        if retries > 0:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            time.sleep(2)
            return self.scrape_katom(model_number, prefix, retries - 1)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
                
    return title, description, specs_data, specs_html, video_links, price, main_image, additional_images

@retry_on_failure(max_attempts=3, delay=2)
def wrapped_scrape_katom(self, model_number, prefix):
    return patched_scrape_katom(self, model_number, prefix)

def patched_process_file(self):
    try:
        file_info = self.get_selected_file()
        if not file_info:
            self.signals.error.emit("No file selected")
            return
        prefix = self.prefix_input.text().strip()
        df = self.load_file_data(file_info)
        
        # Look for the 'Mfr Model' column
        model_col = None
        for col in df.columns:
            if isinstance(col, str) and col.strip().lower() == 'mfr model':
                model_col = col
                break
                
        if not model_col:
            self.signals.error.emit("Missing 'Mfr Model' column in file")
            return
            
        # Define the column ordering - ensure Price is right after Description
        columns = ["Mfr Model"]
        columns.extend(["Manufacturer", "Food Type", "Frypot Style", "Heat", "Hertz", "Nema", 
                        "Number Of Fry Pots", "Oil Capacity/Fryer (Lb)", "Phase", "Product",
                        "Product Type", "Rating", "Special Features", "Type", "Voltage",
                        "Warranty", "Weight", "Dimensions", "Sku"])
        columns.extend(["Shipping Weight"])  # Custom fields
        
        # Add specific columns in the right order
        columns.extend(["Main Image", "Additional Image 1", "Additional Image 2", 
                       "Additional Image 3", "Additional Image 4", "Additional Image 5"])
                       
        # Title, Description and Price in specific order
        columns.extend(["Title", "Description", "Price"])
        
        # Add video links at the end
        for i in range(1, 6):
            columns.append(f"Video Link {i}")
            
        # Remove duplicates while preserving order
        unique_columns = []
        seen = set()
        for col in columns:
            col_lower = col.lower()
            if col_lower not in seen:
                unique_columns.append(col)
                seen.add(col_lower)
                
        # Initialize output DataFrame
        self.output_df = pd.DataFrame(columns=unique_columns)
        self.output_path = os.path.expanduser(f"~/GoogleDriveMount/Web/Completed/Final/final_{prefix}_{file_info['name']}")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Save initial empty results to create the file
        self.save_results()
        
        total_rows = len(df)
        if total_rows == 0:
            self.signals.error.emit("File contains no data rows")
            return
            
        self.signals.update_progress.emit(0, total_rows)
        
        # Process each row
        for i, row_data in df.iterrows():
            if not self.running:
                break
                
            current_row = i + 1
            model = str(row_data[model_col])
            
            if not model or pd.isna(model):
                continue
                
            try:
                self.signals.update_status.emit(f"Processing model: {model}")
                title, desc, specs_dict, specs_html, video_links, price, main_image, additional_images = self.scrape_katom(model, prefix)
                
                if title != "Title not found" and "not found" not in title.lower():
                    combined_description = f'<div style="text-align: justify;">{desc}</div>'
                    if specs_html:
                        combined_description += f'<h3 style="margin-top: 15px;">Specifications</h3>{specs_html}'
                        
                    # Create a new row with all the data
                    row_data = {
                        "Mfr Model": model,
                        "Title": title,
                        "Description": combined_description,
                        "Price": price,
                        "Main Image": main_image
                    }
                    
                    # Add additional images
                    for i, img_url in enumerate(additional_images[:5], 1):
                        row_data[f"Additional Image {i}"] = img_url
                        
                    # Initialize other columns to empty
                    for field in unique_columns:
                        if field not in row_data:
                            row_data[field] = ""
                            
                    # Add specification data
                    for key, value in specs_dict.items():
                        if "weight" in key.lower():
                            value = self.process_weight_value(value)
                            
                        # Try to match the key to a column
                        for field in unique_columns:
                            if key.lower() == field.lower() or key.lower() in field.lower():
                                row_data[field] = value
                                break
                                
                    # Add shipping weight if column exists
                    if "Shipping Weight" in unique_columns:
                        weight = specs_dict.get("weight", "")
                        if weight:
                            row_data["Shipping Weight"] = self.process_weight_value(weight)
                            
                    # Add video links
                    video_list = [link.strip() for link in video_links.strip().split('\n') if link.strip()]
                    for i, link in enumerate(video_list[:5], 1):
                        row_data[f"Video Link {i}"] = link
                        
                    # Ensure output has all required columns
                    for col in unique_columns:
                        if col not in row_data:
                            row_data[col] = ""
                            
                    # Add to dataframe
                    new_row = pd.DataFrame([row_data], columns=unique_columns)
                    self.output_df = pd.concat([self.output_df, new_row], ignore_index=True)
                    self.save_results()
            except Exception as e:
                print(f"Error processing row {current_row}: {e}")
                print(traceback.format_exc())
                
            self.signals.update_progress.emit(current_row, total_rows)
            time.sleep(0.5)
            
        if self.running:
            self.signals.finished.emit()
            
    except Exception as e:
        error_message = str(e)
        print(f"Error in processing: {error_message}")
        print(traceback.format_exc())
        self.signals.error.emit(error_message)

def patched_add_row(self):
    # Import here to avoid the circular import issue
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import QTimer
    
    try:
        # Import SheetRow here to avoid circular import
        from main import SheetRow
        
        row = SheetRow(len(self.scroll_layout), self)
        try:
            from webscraper_wrapper import enhance_row
            enhance_row(row)
            print("Enhanced row with WebScraper Wrapper")
        except ImportError:
            print("WebScraper Wrapper not found, using standard row")
        except Exception as e:
            print(f"Error enhancing row: {e}")
            traceback.print_exc()
        QApplication.processEvents()
        self.scroll_layout.addWidget(row)
        QApplication.processEvents()
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()))
        QTimer.singleShot(500, self.refresh_all_rows)
    except Exception as e:
        print(f"Error adding row: {e}")
        traceback.print_exc()
        QMessageBox.warning(self, "Error", f"Error adding new row: {str(e)}")

def apply_patches():
    """
    Apply all patches to the application components.
    Called from main.py during startup.
    """
    # Import classes from main.py only when needed inside this function
    from main import SheetRow, MainWindow
    
    print("Applying patches to GoogleSheetsProcessor...")
    
    # Backup original methods if needed
    if not hasattr(SheetRow, '_original_extract_table_data'):
        SheetRow._original_extract_table_data = getattr(SheetRow, 'extract_table_data', None)
        
    if not hasattr(SheetRow, '_original_process_weight_value'):
        SheetRow._original_process_weight_value = getattr(SheetRow, 'process_weight_value', None)
        
    if not hasattr(SheetRow, '_original_process_file'):
        SheetRow._original_process_file = getattr(SheetRow, 'process_file', None)
    
    # Apply the patches
    SheetRow.extract_table_data = extract_table_data
    SheetRow.process_weight_value = process_weight_value
    SheetRow.scrape_katom = patched_scrape_katom
    SheetRow.process_file = patched_process_file
    MainWindow.add_row = patched_add_row
    
    print("Patches applied successfully")
    return True

# Used to check if patches are successfully imported
if __name__ == "__main__":
    print("Patches module loaded successfully")
