from playwright.sync_api import sync_playwright
import logging
import time
import os
import sys
import re
import threading

logger = logging.getLogger(__name__)

# Lock to prevent concurrent Playwright sessions
_playwright_lock = threading.Lock()

def download_pdf(referencia_catastral, download_path):
    logger.info("Starting download", extra={"referencia": referencia_catastral})
    
    # Acquire lock to prevent concurrent Playwright sessions
    logger.debug("Acquiring Playwright lock")
    _playwright_lock.acquire()
    logger.debug("Playwright lock acquired")
    
    browser = None
    context = None
    
    try:
        with sync_playwright() as p:
            # Launch the browser in headless mode
            logger.debug("Launching browser")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            
            # Create a new page
            page = context.new_page()
            
            try:
                # Navigate to the URL
                base_url = "https://muib.caib.es/mapurbibfront/visor_index.jsp#"
                logger.info("Navigating to base URL", extra={"url": base_url})
                page.goto(base_url, timeout=60000)
                
                # Wait for the page to load completely
                logger.debug("Waiting for page to load")
                page.wait_for_load_state('networkidle', timeout=60000)
                
                # Wait for the checkboxes to be present and handle them
                logger.debug("Handling layer checkboxes")
                page.wait_for_selector('#MUIB0Checkbox', timeout=30000)
                page.wait_for_selector('#MUIB1Checkbox', timeout=30000)
                
                # Uncheck MUIB0Checkbox
                logger.debug("Unchecking MUIB0 layer")
                page.uncheck('#MUIB0Checkbox')
                
                # Check MUIB1Checkbox
                logger.debug("Checking MUIB1 layer")
                page.check('#MUIB1Checkbox')
                
                # Wait for the changes to take effect
                time.sleep(2)
                
                # Click on the cadastre panel to expand it
                logger.debug("Expanding cadastre panel")
                page.wait_for_selector('#cadastre', timeout=30000)
                page.click('#cadastre .x-panel-header')
                
                # Wait for the panel to expand
                time.sleep(1)
                
                # Wait for the refcat input field and enter the referencia catastral
                logger.info("Entering referencia catastral", extra={"referencia": referencia_catastral})
                page.wait_for_selector('#refcat', timeout=30000)
                page.fill('#refcat', referencia_catastral)
                
                # Retry logic for search - try up to 2 times
                max_search_retries = 2
                search_success = False
                
                for attempt in range(1, max_search_retries + 1):
                    logger.info(f"Search attempt {attempt}/{max_search_retries}")
                    
                    # Click the search button using the correct selector
                    logger.debug("Clicking search button")
                    page.click('input[type="button"][onclick="cercarRefCat();"]')
                    
                    # Wait for results to load
                    logger.debug("Waiting for network to be idle after search")
                    try:
                        page.wait_for_load_state('networkidle', timeout=30000)
                    except Exception as e:
                        logger.warning(f"Network idle wait timed out on attempt {attempt}", extra={"error": str(e)})
                    
                    # Wait for the result panel
                    logger.debug("Waiting for result panel")
                    try:
                        page.wait_for_selector('#resultat', timeout=10000)
                    except Exception as e:
                        logger.warning(f"Result panel not found on attempt {attempt}", extra={"error": str(e)})
                        if attempt < max_search_retries:
                            logger.info("Retrying search...")
                            time.sleep(2)
                            continue
                        else:
                            raise
                    
                    # Check if result panel has content
                    result_panel = page.locator('#resultat')
                    result_text = ""
                    result_html = ""
                    if result_panel.count() > 0:
                        try:
                            result_text = result_panel.inner_text(timeout=5000)
                            result_html = result_panel.inner_html(timeout=5000)
                        except:
                            pass
                    
                    logger.debug(f"Result panel content length: {len(result_text)}, HTML length: {len(result_html)}")
                    if result_text:
                        logger.debug(f"Result panel text preview: {result_text[:200]}")
                    
                    # Check if result panel contains error messages
                    error_indicators = ["error", "no se encontró", "no encontrado", "sin resultados", "not found"]
                    result_lower = result_text.lower() if result_text else ""
                    has_error = any(indicator in result_lower for indicator in error_indicators)
                    
                    if has_error and result_text:
                        logger.error(f"Error detected in result panel: {result_text[:500]}")
                        raise Exception(f"Search returned an error: {result_text[:200]}")
                    
                    # Wait for the result link to appear with increased timeout
                    logger.debug("Waiting for result link", extra={"timeout": 60000})
                    try:
                        page.wait_for_selector('a[onclick^="situarRefCat"]', timeout=60000)
                        logger.info("Result link found successfully")
                        search_success = True
                        break
                    except Exception as e:
                        logger.warning(f"Result link not found on attempt {attempt}", extra={"error": str(e)})
                        if result_text:
                            logger.warning(f"Result panel contains: {result_text[:500]}")
                        
                        # If we have content but no link, it might be an error - don't retry
                        if result_text and len(result_text) > 50 and not has_error:
                            logger.warning("Result panel has content but no link - might be a different error format")
                        
                        if attempt < max_search_retries:
                            # Take a screenshot for debugging
                            try:
                                screenshot_path = f"/tmp/search_failure_attempt_{attempt}.png"
                                page.screenshot(path=screenshot_path)
                                logger.debug(f"Screenshot saved to {screenshot_path}")
                            except Exception as screenshot_error:
                                logger.debug(f"Could not save screenshot: {screenshot_error}")
                            
                            logger.warning(f"Result panel HTML length: {len(result_html)}")
                            
                            logger.info("Retrying search from beginning...")
                            # Reload the page and start over
                            page.goto(base_url, timeout=60000)
                            page.wait_for_load_state('networkidle', timeout=60000)
                            page.wait_for_selector('#MUIB0Checkbox', timeout=30000)
                            page.wait_for_selector('#MUIB1Checkbox', timeout=30000)
                            page.uncheck('#MUIB0Checkbox')
                            page.check('#MUIB1Checkbox')
                            time.sleep(2)
                            page.wait_for_selector('#cadastre', timeout=30000)
                            page.click('#cadastre .x-panel-header')
                            time.sleep(1)
                            page.wait_for_selector('#refcat', timeout=30000)
                            page.fill('#refcat', referencia_catastral)
                            time.sleep(1)
                            continue
                        else:
                            raise
                
                if not search_success:
                    raise Exception("Failed to find result link after all retry attempts")
                
                # Click the result link
                logger.debug("Clicking result link")
                page.click('a[onclick^="situarRefCat"]')
                
                # Wait for the map to update
                time.sleep(2)
                
                # Click the info button
                logger.debug("Clicking info button")
                page.wait_for_selector('button.x-btn-text.info', timeout=30000)
                page.click('button.x-btn-text.info')
                
                # Wait for the map div and click its center
                logger.debug("Waiting for map div")
                try:
                    # Wait for the map div to be visible
                    page.wait_for_selector('#ext-gen109', timeout=10000)
                    
                    # Get the map div and click its center
                    logger.debug("Calculating map div center")
                    map_div = page.locator('#ext-gen109')
                    
                    # Wait a bit for the map to be fully rendered
                    time.sleep(2)
                    
                    # Get the bounding box
                    map_box = map_div.bounding_box()
                    
                    if map_box:
                        # Calculate center position
                        center_x = map_box['x'] + (map_box['width'] / 2)
                        center_y = map_box['y'] + (map_box['height'] / 2)
                        logger.debug(
                            "Map div center located",
                            extra={"center_x": center_x, "center_y": center_y}
                        )
                        
                        # Click at the center
                        logger.debug("Clicking map center")
                        page.mouse.click(center_x, center_y)
                    else:
                        logger.warning("Could not get map div position, using fallback click")
                        # Try clicking at a fixed position as fallback
                        logger.info("Clicking fallback map position")
                        page.mouse.click(300, 400)  # Click near the center of the typical map size
                except Exception as e:
                    logger.warning("Failed to calculate map div center, using fallback", extra={"error": str(e)})
                    # Try clicking at a fixed position as fallback
                    logger.info("Clicking fallback map position")
                    page.mouse.click(300, 400)  # Click near the center of the typical map size
                
                # Wait for the info to load
                time.sleep(2)
                
                # Click on the Fitxa link
                logger.debug("Clicking Fitxa link")
                page.wait_for_selector('a[onclick="obrirFitxa();"]', timeout=30000)
                page.click('a[onclick="obrirFitxa();"]')
                
                # Wait for the new tab to open
                logger.debug("Waiting for Fitxa window")
                new_page = context.wait_for_event('page')
                
                # Wait for the new page to load
                new_page.wait_for_load_state('networkidle', timeout=60000)
                
                # Wait for the content to be fully loaded
                logger.debug("Waiting for Fitxa content")
                # Wait for any of these possible content indicators
                try:
                    new_page.wait_for_selector('.x-panel-body', timeout=5000)
                except:
                    try:
                        new_page.wait_for_selector('.x-window-body', timeout=5000)
                    except:
                        try:
                            new_page.wait_for_selector('.x-panel', timeout=5000)
                        except:
                            logger.debug("Generic content wait for Fitxa page")
                
                # Additional wait to ensure all dynamic content is loaded
                time.sleep(3)
                
                # Generate PDF using Playwright's pdf() function
                logger.info("Generating PDF", extra={"referencia": referencia_catastral, "path": download_path})
                new_page.pdf(
                    path=download_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "20px", "right": "20px", "bottom": "20px", "left": "20px"}
                )
                
                logger.info("PDF successfully saved", extra={"path": download_path})
                
            except Exception as e:
                logger.exception("Playwright automation failed", extra={"referencia": referencia_catastral})
                raise  # Re-raise the exception to be handled by the Flask app
            
            finally:
                # Ensure proper cleanup: close context first, then browser
                if context:
                    try:
                        logger.debug("Closing browser context")
                        context.close()
                    except Exception as e:
                        logger.warning("Error closing context", extra={"error": str(e)})
                
                if browser:
                    try:
                        logger.debug("Closing browser")
                        browser.close()
                    except Exception as e:
                        logger.warning("Error closing browser", extra={"error": str(e)})
                
                logger.debug("Browser cleanup completed")
    
    finally:
        # Always release the lock
        _playwright_lock.release()
        logger.debug("Playwright lock released")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )
    if len(sys.argv) != 2:
        print("Usage: python fitxa_muib_downloader.py <referencia_catastral>")
        sys.exit(1)
        
    referencia_catastral = sys.argv[1]
    output_path = f"{referencia_catastral}.pdf"
    
    download_pdf(referencia_catastral, output_path)