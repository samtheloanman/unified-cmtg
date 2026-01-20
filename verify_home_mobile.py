from playwright.sync_api import sync_playwright
import time

def verify(page):
    print("Navigating to home page...")
    page.goto("http://localhost:3000")

    print("Waiting for h1...")
    try:
        page.wait_for_selector("h1", timeout=10000)
    except:
        print("Timeout waiting for h1. Page content:")
        print(page.content())
        raise

    # Check font family of h1
    h1 = page.locator("h1")
    font_family = h1.evaluate("el => window.getComputedStyle(el).fontFamily")
    print(f"H1 Font Family: {font_family}")

    # Screenshot desktop
    page.screenshot(path="verification_desktop.png")
    print("Desktop screenshot saved.")

    # Mobile
    page.set_viewport_size({"width": 375, "height": 667})
    # Wait a bit for layout to adjust
    time.sleep(1)
    page.screenshot(path="verification_mobile.png")
    print("Mobile screenshot saved.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify(page)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()
