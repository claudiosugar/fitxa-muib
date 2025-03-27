from playwright.sync_api import sync_playwright
import time
import os
import sys
import re

def download_pdf(referencia_catastral, download_path):
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=False)  # Set to True if you don't want to see the browser
        context = browser.new_context(
            accept_downloads=True  # Enable downloads
        )
        
        # Create a new page
        page = context.new_page()
        
        try:
            # Navigate to the URL
            base_url = "https://muib.caib.es/mapurbibfront/visor_index.jsp#"
            print(f"Navigating to {base_url}...")
            page.goto(base_url)
            
            # Wait for the page to load completely
            page.wait_for_load_state('networkidle')
            
            # Wait for the checkboxes to be present and handle them
            print("Handling layer checkboxes...")
            page.wait_for_selector('#MUIB0Checkbox')
            page.wait_for_selector('#MUIB1Checkbox')
            
            # Uncheck MUIB0Checkbox
            print("Unchecking MUIB0Checkbox...")
            page.uncheck('#MUIB0Checkbox')
            
            # Check MUIB1Checkbox
            print("Checking MUIB1Checkbox...")
            page.check('#MUIB1Checkbox')
            
            # Wait for the changes to take effect
            time.sleep(2)
            
            # Click on the cadastre panel to expand it
            print("Expanding cadastre panel...")
            page.wait_for_selector('#cadastre')
            page.click('#cadastre .x-panel-header')
            
            # Wait for the panel to expand
            time.sleep(1)
            
            # Wait for the refcat input field and enter the referencia catastral
            print(f"Entering referencia catastral: {referencia_catastral}")
            page.wait_for_selector('#refcat')
            page.fill('#refcat', referencia_catastral)
            
            # Click the search button using the correct selector
            print("Clicking search button...")
            page.click('input[type="button"][onclick="cercarRefCat();"]')
            
            # Wait for results to load
            page.wait_for_load_state('networkidle')
            
            # Wait for the result panel and click on the result link
            print("Waiting for result and clicking on it...")
            page.wait_for_selector('#resultat')
            
            # Wait for the result link to appear and click it
            # We'll wait for any link that contains the onclick="situarRefCat" attribute
            page.wait_for_selector('a[onclick^="situarRefCat"]')
            page.click('a[onclick^="situarRefCat"]')
            
            # Wait for the map to update
            time.sleep(2)
            
            # Click the info button
            print("Clicking info button...")
            page.wait_for_selector('button.x-btn-text.info')
            page.click('button.x-btn-text.info')
            
            # Wait for the map div and click its center
            print("Waiting for map div...")
            try:
                # Wait for the map div to be visible
                page.wait_for_selector('#ext-gen109', timeout=10000)
                
                # Get the map div and click its center
                print("Getting map div position...")
                map_div = page.locator('#ext-gen109')
                
                # Wait a bit for the map to be fully rendered
                time.sleep(2)
                
                # Get the bounding box
                map_box = map_div.bounding_box()
                
                if map_box:
                    # Calculate center position
                    center_x = map_box['x'] + (map_box['width'] / 2)
                    center_y = map_box['y'] + (map_box['height'] / 2)
                    print(f"Map div center position: ({center_x}, {center_y})")
                    
                    # Click at the center
                    print("Clicking at map div center...")
                    page.mouse.click(center_x, center_y)
                else:
                    print("Could not get map div position")
                    # Try clicking at a fixed position as fallback
                    print("Trying fallback click position...")
                    page.mouse.click(300, 400)  # Click near the center of the typical map size
            except Exception as e:
                print(f"Error getting map div: {str(e)}")
                # Try clicking at a fixed position as fallback
                print("Trying fallback click position...")
                page.mouse.click(300, 400)  # Click near the center of the typical map size
            
            # Wait for the info to load
            time.sleep(2)
            
            # Wait for and click the download PDF button
            print("Waiting for download button...")
            with page.expect_download() as download_info:
                page.click('button:has-text("PDF")')
            
            download = download_info.value
            
            # Save the downloaded file
            print(f"Saving PDF to {download_path}...")
            download.save_as(download_path)
            
            print(f"PDF successfully downloaded to {download_path}")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
        finally:
            # Close the browser
            browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pdf_downloader.py <referencia_catastral>")
        sys.exit(1)
        
    referencia_catastral = sys.argv[1]
    output_path = f"{referencia_catastral}.pdf"
    
    download_pdf(referencia_catastral, output_path) 