import json
import os

try:
    with open('unified-platform/backend/wp_export/pages.json', 'r') as f:
        data = json.load(f)
        
    print(f"Total Pages in Export: {len(data)}")
    print("| Title | Slug | Status |")
    print("| :--- | :--- | :--- |")
    
    count = 0
    for page in data:
        # Check if it has a title
        title = page.get('title', {}).get('rendered', 'No Title')
        slug = page.get('slug', 'no-slug')
        status = page.get('status', 'unknown')
        
        # Filter out trivial pages if needed, but user wants "complete list"
        print(f"| {title} | {slug} | {status} |")
        count += 1
        
    print(f"\nTotal Listed: {count}")

except Exception as e:
    print(f"Error: {e}")
