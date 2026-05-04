import asyncio
from playwright.async_api import async_playwright
from datetime import datetime

import sys

async def retrieve_i94_history(first_name: str, last_name: str, dob: str, passport_number: str, country_of_citizenship: str, output_path: str = "i94_history.pdf"):
    """
    Automates the retrieval of I-94 travel history from the CBP website.
    dob format: 'YYYY-MM-DD'
    """
    print(f"Starting I-94 retrieval for {first_name} {last_name}...")
    
    async with async_playwright() as p:
        headless_mode = sys.platform != 'win32'
        browser = await p.chromium.launch(headless=headless_mode)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # 1. Navigate directly to the I-94 history search page
            print("Navigating to CBP I-94 history search...")
            await page.goto("https://i94.cbp.dhs.gov/search/history-search", wait_until="networkidle")
            
            # 2. Accept the Terms of Service security notification
            print("Accepting security notification...")
            # We add a small timeout so it doesn't block forever if the modal doesn't appear
            try:
                await page.wait_for_selector('mat-dialog-content', state='visible', timeout=10000)
                await page.locator('mat-dialog-content').evaluate('node => node.scrollTop = node.scrollHeight')
                await page.locator('button#consent-btn').click()
            except Exception:
                print("Security modal not found or skipped. Continuing...")
            
            # 3. Fill in the traveler information
            print("Filling in traveler information...")
            
            # Format DOB as MM/DD/YYYY
            dob_obj = datetime.strptime(dob, "%Y-%m-%d")
            formatted_dob = dob_obj.strftime("%m/%d/%Y")

            await page.locator('input#first-name').fill(first_name)
            await page.locator('input#last-name').fill(last_name)
            await page.locator('input#birth-date').fill(formatted_dob)
            
            # Document details
            await page.locator('input#document-number').fill(passport_number)
            
            # Country of Issuance (Autocomplete field)
            await page.locator('input#mat-input-3').fill("India")
            await page.wait_for_timeout(1000)
            # Wait for the autocomplete option to appear and click it
            await page.get_by_text("India (IND)", exact=True).click()
            
            # 4. Submit the form
            print("Submitting the form...")
            await page.locator('button#submit-travel-history').click()
            
            print("Waiting for results...")
            await page.wait_for_timeout(8000) # Wait a bit longer for the search to complete
            
            page_text = await page.locator("body").inner_text()
            status_msg = ""
            if "No record found" in page_text or "not found" in page_text.lower() or "No travel history" in page_text:
                status_msg = "STATUS: No travel history found for this traveler."
            else:
                status_msg = "STATUS: Travel history retrieved successfully."
            print(status_msg)
            
            # If the user requested a PDF extension, change it to PNG
            if output_path.endswith(".pdf"):
                output_path = output_path.replace(".pdf", ".png")
            
            print(f"Saving screenshot to {output_path}...")
            await page.screenshot(path=output_path, full_page=True)
            
            print(f"[SUCCESS] {status_msg} Saved screenshot to {output_path}")
            
        except Exception as e:
            print(f"[ERROR] An error occurred: {e}")
        
        finally:
            print("Closing browser...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(retrieve_i94_history(
        first_name="SRINIJH REDDY",
        last_name="CHENDI",
        dob="2000-11-08",
        passport_number="U9212755",
        country_of_citizenship="India (IND)",
        output_path="I94_Travel_History_Srinijh.png"
    ))
