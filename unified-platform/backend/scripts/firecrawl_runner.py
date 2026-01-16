import requests
import time
import json
import os
import sys

# Configuration
FIRECRAWL_API = "http://localhost:3002"
TARGET_URL = "https://custommortgageinc.com"
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "../wp_export/firecrawl_dump.json")

def wait_for_api():
    print(f"Waiting for Firecrawl API at {FIRECRAWL_API}...")
    retries = 30
    while retries > 0:
        try:
            response = requests.get(f"{FIRECRAWL_API}/test") # or just root
            # The root often returns a welcome message or 404, but connection is what matters.
            # Official health check might be /health or similar.
            # Let's try to connect; if we get a response (even 404), the server is up.
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            retries -= 1
            print(".", end="", flush=True)
    print("\nTimeout waiting for API.")
    return False

def start_crawl():
    print(f"\nStarting crawl for {TARGET_URL}...")
    headers = {"Content-Type": "application/json"}
    payload = {
        "url": TARGET_URL,
        "limit": 5000,
        "maxDepth": 10,
        "scrapeOptions": {
            "formats": ["markdown", "html"],
            "onlyMainContent": True
        }
    }
    
    try:
        response = requests.post(f"{FIRECRAWL_API}/v1/crawl", json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        job_id = data.get("id") or data.get("jobId")
        print(f"Job started! ID: {job_id}")
        return job_id
    except Exception as e:
        print(f"Error starting crawl: {e}")
        # Try to print response text if available
        if 'response' in locals():
             print(f"Response: {response.text}")
        sys.exit(1)

def poll_crawl(job_id):
    print(f"Polling job {job_id}...")
    status = "active"
    
    while status not in ["completed", "failed", "cancelled"]:
        try:
            response = requests.get(f"{FIRECRAWL_API}/v1/crawl/{job_id}")
            response.raise_for_status()
            data = response.json()
            status = data.get("status")
            completed = data.get("completed", 0)
            total = data.get("total", 0)
            credits = data.get("creditsUsed", 0)
            
            print(f"Status: {status} | Pages: {completed}/{total} | Credits: {credits}")
            
            if status == "completed":
                return data
            elif status == "failed":
                print("Crawl failed!")
                sys.exit(1)
            
            time.sleep(2)
        except Exception as e:
            print(f"Error polling: {e}")
            time.sleep(5)

def save_data(data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\n✅ Crawl data saved to {OUTPUT_FILE}")
    print(f"Total pages: {len(data.get('data', []))}")

if __name__ == "__main__":
    if not wait_for_api():
        sys.exit(1)
        
    job_id = start_crawl()
    if job_id:
        result = poll_crawl(job_id)
        save_data(result)
