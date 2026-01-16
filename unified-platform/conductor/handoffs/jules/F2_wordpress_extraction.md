# Jules Prompt: Phase F.2 - WordPress Content Extraction

**Track**: `finalization_20260114`  
**Phase**: F.2  
**Priority**: HIGH  
**Estimated Time**: 2-3 hours  
**Can Run Parallel With**: F.4

---

## MISSION

Extract all content from WordPress (custommortgageinc.com) using REST API. Export to JSON files for import into Wagtail.

## CONTEXT

- WordPress site: `https://custommortgageinc.com`
- Uses Advanced Custom Fields (ACF) for program data
- Need to extract: Programs, Funded Loans, Blog Posts, Media
- Output will be used by F.3 (Content Import)

## REFERENCE FILES

- PRD: `prd.md` Section 6.1 (Data Models)
- Phase 3 Content Plan: `conductor/tracks/phase3_content/plan.md`
- Target field mapping: See ProgramPage model created in F.1

## TASKS

### 1. Create WordPress Extractor Script

**File**: `backend/scripts/wp_extractor.py`

```python
import requests
import json
from pathlib import Path
from typing import List, Dict
import time

class WordPressExtractor:
    """Extract content from WordPress REST API."""
    
    BASE_URL = "https://custommortgageinc.com/wp-json"
    
    def __init__(self, output_dir: str = "wp_export"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
    
    def get_all_posts(self, post_type: str, params: dict = None) -> List[Dict]:
        """Fetch all posts of a type with pagination."""
        posts = []
        page = 1
        base_params = {'per_page': 100, 'acf_format': 'standard'}
        if params:
            base_params.update(params)
        
        while True:
            base_params['page'] = page
            url = f"{self.BASE_URL}/wp/v2/{post_type}"
            
            try:
                response = self.session.get(url, params=base_params, timeout=30)
                
                if response.status_code == 400:  # No more pages
                    break
                    
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                    
                posts.extend(data)
                print(f"  Fetched page {page}: {len(data)} items")
                page += 1
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"  Error on page {page}: {e}")
                break
        
        return posts
    
    def extract_programs(self) -> List[Dict]:
        """Extract all program posts with ACF data."""
        print("Extracting programs...")
        # Try both 'programs' and 'program' endpoints
        programs = self.get_all_posts('programs')
        if not programs:
            programs = self.get_all_posts('program')
        
        with open(self.output_dir / 'programs.json', 'w') as f:
            json.dump(programs, f, indent=2)
        
        print(f"  Exported {len(programs)} programs")
        return programs
    
    def extract_funded_loans(self) -> List[Dict]:
        """Extract funded loan showcase posts."""
        print("Extracting funded loans...")
        loans = self.get_all_posts('funded-loans')
        if not loans:
            loans = self.get_all_posts('funded_loans')
        
        with open(self.output_dir / 'funded_loans.json', 'w') as f:
            json.dump(loans, f, indent=2)
        
        print(f"  Exported {len(loans)} funded loans")
        return loans
    
    def extract_blogs(self) -> List[Dict]:
        """Extract blog posts."""
        print("Extracting blog posts...")
        posts = self.get_all_posts('posts')
        
        with open(self.output_dir / 'blogs.json', 'w') as f:
            json.dump(posts, f, indent=2)
        
        print(f"  Exported {len(posts)} blog posts")
        return posts
    
    def generate_url_mapping(self, programs: List[Dict]) -> None:
        """Generate CSV mapping WordPress URLs to Wagtail slugs."""
        print("Generating URL mapping...")
        
        with open(self.output_dir / 'url_mapping.csv', 'w') as f:
            f.write("wordpress_url,wagtail_slug,content_type\n")
            
            for program in programs:
                wp_url = program.get('link', '')
                slug = program.get('slug', '')
                f.write(f"{wp_url},{slug},program\n")
        
        print(f"  Generated URL mapping for {len(programs)} items")
    
    def run(self):
        """Run full extraction."""
        print("=" * 50)
        print("WordPress Content Extraction")
        print("=" * 50)
        
        programs = self.extract_programs()
        self.extract_funded_loans()
        self.extract_blogs()
        self.generate_url_mapping(programs)
        
        print("=" * 50)
        print("Extraction complete!")
        print(f"Output directory: {self.output_dir.absolute()}")


if __name__ == '__main__':
    extractor = WordPressExtractor()
    extractor.run()
```

### 2. Run the Extraction

```bash
cd unified-platform/backend
python scripts/wp_extractor.py
```

### 3. Verify Output

Check generated files:
```bash
# Count programs
jq length wp_export/programs.json

# Check ACF fields present
jq '.[0].acf | keys' wp_export/programs.json

# Check funded loans
jq length wp_export/funded_loans.json

# Check blogs
jq length wp_export/blogs.json

# View URL mapping
head wp_export/url_mapping.csv
```

### 4. Handle Edge Cases

If WordPress REST API requires authentication:
```python
# Add to __init__
self.session.auth = ('username', 'password')
# Or use application password/API key
```

If ACF fields are not included:
- Check if ACF REST API plugin is enabled
- Try adding `?_fields=acf,title,slug,link` to requests

## SUCCESS CRITERIA

- [ ] `wp_export/programs.json` contains 75+ programs
- [ ] Each program has `acf` field with custom data
- [ ] `wp_export/funded_loans.json` created
- [ ] `wp_export/blogs.json` created
- [ ] `wp_export/url_mapping.csv` generated
- [ ] No errors during extraction

## HANDOFF

After completion, write to `conductor/handoffs/gemini/inbox.md`:
```
F.2 Complete: Extracted [X] programs, [Y] funded loans, [Z] blogs from WordPress.
ACF fields captured. URL mapping generated.
Ready for F.3 (Content Import).
```

Commit: `git commit -m "feat(cms): F.2 WordPress content extraction"`
