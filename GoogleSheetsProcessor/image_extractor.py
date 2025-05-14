#!/usr/bin/env python3
# image_extractor.py - Add image extraction capabilities to the scraper

import os
import re
import traceback
from selenium.webdriver.common.by import By

def extract_images(driver):
    """Extract main image and additional images from the page"""
    main_image = ""
    additional_images = []
    
    try:
        print("Looking for images on the page...")
        
        # First attempt: Look for product images using common selectors
        product_images = driver.find_elements(By.CSS_SELECTOR, 
            ".product-image img, #product-image img, #main-image img, .main-image img, [class*='product'] img, [id*='product'] img")
        
        # Second attempt: Look for gallery images
        if not product_images:
            product_images = driver.find_elements(By.CSS_SELECTOR, 
                ".gallery img, .product-gallery img, #gallery img, [class*='gallery'] img, .carousel img")
        
        # Third attempt: Look for any large images
        if not product_images:
            all_images = driver.find_elements(By.TAG_NAME, "img")
            # Filter for larger images (likely product images, not icons)
            product_images = [img for img in all_images if 
                              img.get_attribute("width") and int(img.get_attribute("width") or 0) > 200]
        
        # Final attempt: Just get all images if nothing else worked
        if not product_images:
            product_images = driver.find_elements(By.TAG_NAME, "img")
        
        print(f"Found {len(product_images)} potential product images")
        
        # If we have images, process them
        if product_images:
            # Try to identify the main image (usually the first one or the largest)
            for img in product_images:
                src = img.get_attribute("src")
                if not src:
                    continue
                    
                # Skip small images, icons, or logos
                if src.lower().endswith(('.ico', '.svg')) or 'icon' in src.lower() or 'logo' in src.lower():
                    continue
                
                # If we don't have a main image yet, set this as main
                if not main_image:
                    main_image = src
                    print(f"Selected main image: {src}")
                else:
                    # Add other images as additional
                    if src != main_image and src not in additional_images:
                        additional_images.append(src)
                        print(f"Added additional image: {src}")
                
                # Limit to 5 additional images
                if len(additional_images) >= 5:
                    break
        
        # Look for images in the page source if nothing found
        if not main_image:
            print("Searching for images in page source...")
            page_source = driver.page_source
            # Look for image URLs in the source - fixed the syntax error here
            img_pattern = r'https?://[^"\']+\.(jpg|jpeg|png|gif|webp)'
            matches = re.findall(img_pattern, page_source)
            
            if matches:
                for match in matches:
                    url = match  # In regex matches, this should be the first group
                    if isinstance(url, tuple):
                        url = url[0]  # If it's a tuple, get the full URL
                    
                    # Skip small images, icons, or logos
                    if 'icon' in url.lower() or 'logo' in url.lower():
                        continue
                    
                    if not main_image:
                        main_image = url
                        print(f"Found main image in source: {url}")
                    elif url != main_image and url not in additional_images:
                        additional_images.append(url)
                        print(f"Found additional image in source: {url}")
                    
                    # Limit to 5 additional images
                    if len(additional_images) >= 5:
                        break
    
    except Exception as e:
        print(f"Error extracting images: {e}")
        print(traceback.format_exc())
    
    return main_image, additional_images
