#!/usr/bin/env python3
"""
WordPress Content Extraction Script
====================================
Extracts content from WordPress REST API and prepares for Wagtail migration.

Usage:
    python wp_extractor.py [--base-url URL] [--output-dir DIR]

Features:
- Extracts programs, funded loans, and blog posts via REST API
- Downloads media files with progress tracking
- Generates URL mapping CSV for migration verification
- Handles pagination automatically
- Includes ACF data when available
- Error handling with retries
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class WordPressExtractor:
    """Extracts content from WordPress via REST API"""
    
    def __init__(self, base_url: str, output_dir: str = "wp_export", per_page: int = 20, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.output_dir = Path(output_dir)
        self.media_dir = Path("media/wp_import")
        self.per_page = per_page
        self.timeout = timeout
        
        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup session with retries
        self.session = self._create_session()
        
        # Stats tracking
        self.stats = {
            'programs': 0,
            'funded_loans': 0,
            'blogs': 0,
            'media_files': 0,
            'errors': []
        }
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _get_paginated(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """Fetch all pages from a paginated endpoint"""
        if params is None:
            params = {}
        
        params['per_page'] = self.per_page
        params['page'] = 1
        
        all_items = []
        
        while True:
            try:
                print(f"  Fetching page {params['page']} (size: {self.per_page})...", end=' ')
                response = self.session.get(
                    f"{self.api_url}/{endpoint}",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                items = response.json()
                if not items:
                    print("(empty)")
                    break
                
                all_items.extend(items)
                print(f"({len(items)} items)")
                
                # Check if there are more pages
                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                if params['page'] >= total_pages:
                    break
                
                params['page'] += 1
                time.sleep(0.5)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Error fetching {endpoint} page {params['page']}: {e}"
                print(f"\n  ❌ {error_msg}")
                self.stats['errors'].append(error_msg)
                break
        
        return all_items
    
    def extract_programs(self) -> List[Dict]:
        """Extract all program posts"""
        print("\n📦 Extracting Programs...")
        
        # Try multiple post type names (different WordPress setups may use different names)
        for post_type in ['program', 'loan-programs', 'loan_programs']:
            try:
                programs = self._get_paginated(post_type, {'acf_format': 'standard'})
                if programs:
                    print(f"  ✅ Found {len(programs)} programs (post_type: {post_type})")
                    self.stats['programs'] = len(programs)
                    
                    # Save to JSON
                    output_file = self.output_dir / 'programs.json'
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(programs, f, indent=2, ensure_ascii=False)
                    print(f"  💾 Saved to {output_file}")
                    
                    return programs
            except Exception as e:
                print(f"  ⚠️  Post type '{post_type}' not found or error: {e}")
                continue
        
        print("  ⚠️  No programs found")
        return []
    
    def extract_funded_loans(self) -> List[Dict]:
        """Extract all funded loan posts"""
        print("\n📦 Extracting Funded Loans...")
        
        try:
            funded_loans = self._get_paginated('funded-loan', {'acf_format': 'standard'})
            if funded_loans:
                print(f"  ✅ Found {len(funded_loans)} funded loans")
                self.stats['funded_loans'] = len(funded_loans)
                
                # Save to JSON
                output_file = self.output_dir / 'funded_loans.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(funded_loans, f, indent=2, ensure_ascii=False)
                print(f"  💾 Saved to {output_file}")
                
                return funded_loans
        except Exception as e:
            error_msg = f"Error extracting funded loans: {e}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
        
        return []
    
    def extract_blogs(self) -> List[Dict]:
        """Extract all blog posts"""
        print("\n📦 Extracting Blog Posts...")
        
        try:
            blogs = self._get_paginated('posts', {'acf_format': 'standard'})
            if blogs:
                print(f"  ✅ Found {len(blogs)} blog posts")
                self.stats['blogs'] = len(blogs)
                
                # Save to JSON
                output_file = self.output_dir / 'blogs.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(blogs, f, indent=2, ensure_ascii=False)
                print(f"  💾 Saved to {output_file}")
                
                return blogs
        except Exception as e:
            error_msg = f"Error extracting blogs: {e}"
            print(f"  ❌ {error_msg}")
            self.stats['errors'].append(error_msg)
        
        return []
    
    def download_media(self, content_items: List[List[Dict]]) -> Dict[str, str]:
        """Download media files referenced in content
        
        Args:
            content_items: List of lists containing content items
            
        Returns:
            Dictionary mapping original URLs to local file paths
        """
        print("\n📥 Downloading Media Files...")
        
        media_map = {}
        media_urls = set()
        
        # Collect all media URLs from content
        for items in content_items:
            for item in items:
                # Check featured_media
                if 'featured_media' in item and item['featured_media']:
                    media_urls.add(item['featured_media'])
                
                # Check ACF fields for images
                if 'acf' in item and isinstance(item['acf'], dict):
                    self._extract_media_from_acf(item['acf'], media_urls)
        
        print(f"  Found {len(media_urls)} unique media references")
        
        # Download each media file
        for i, media_id in enumerate(media_urls, 1):
            if isinstance(media_id, int):
                try:
                    # Get media info from API
                    response = self.session.get(
                        f"{self.api_url}/media/{media_id}",
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        media = response.json()
                        source_url = media.get('source_url')
                        
                        if source_url:
                            local_path = self._download_file(source_url)
                            if local_path:
                                media_map[source_url] = local_path
                                print(f"  [{i}/{len(media_urls)}] ✅ Downloaded: {Path(source_url).name}")
                            else:
                                print(f"  [{i}/{len(media_urls)}] ❌ Failed: {Path(source_url).name}")
                    
                    time.sleep(0.3)  # Rate limiting
                    
                except Exception as e:
                    error_msg = f"Error downloading media {media_id}: {e}"
                    print(f"  ❌ {error_msg}")
                    self.stats['errors'].append(error_msg)
        
        # Save media manifest
        manifest_file = self.output_dir / 'media_manifest.json'
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(media_map, f, indent=2, ensure_ascii=False)
        
        self.stats['media_files'] = len(media_map)
        print(f"  💾 Saved media manifest to {manifest_file}")
        print(f"  ✅ Downloaded {len(media_map)} media files")
        
        return media_map
    
    def _extract_media_from_acf(self, acf_data: Dict, media_urls: set):
        """Recursively extract media URLs from ACF data"""
        for key, value in acf_data.items():
            if isinstance(value, dict):
                if 'url' in value and isinstance(value.get('id'), int):
                    # This looks like an ACF image field
                    media_urls.add(value['id'])
                else:
                    self._extract_media_from_acf(value, media_urls)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._extract_media_from_acf(item, media_urls)
    
    def _download_file(self, url: str) -> Optional[str]:
        """Download a file from URL to local media directory"""
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Parse filename from URL
            parsed_url = urllib.parse.urlparse(url)
            filename = Path(parsed_url.path).name
            
            # Save to media directory
            filepath = self.media_dir / filename
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return str(filepath)
            
        except Exception as e:
            self.stats['errors'].append(f"Download error for {url}: {e}")
            return None
    
    def generate_url_mapping(self, programs: List[Dict], funded_loans: List[Dict], blogs: List[Dict]):
        """Generate URL mapping CSV for migration verification"""
        print("\n🔗 Generating URL Mapping...")
        
        url_mappings = []
        
        # Process programs
        for program in programs:
            url_mappings.append({
                'content_type': 'program',
                'post_id': program.get('id'),
                'title': program.get('title', {}).get('rendered', ''),
                'slug': program.get('slug', ''),
                'old_url': program.get('link', ''),
                'new_url': f"/programs/{program.get('slug', '')}/",
            })
        
        # Process funded loans
        for loan in funded_loans:
            url_mappings.append({
                'content_type': 'funded-loan',
                'post_id': loan.get('id'),
                'title': loan.get('title', {}).get('rendered', ''),
                'slug': loan.get('slug', ''),
                'old_url': loan.get('link', ''),
                'new_url': f"/funded-loans/{loan.get('slug', '')}/",
            })
        
        # Process blogs
        for blog in blogs:
            url_mappings.append({
                'content_type': 'blog',
                'post_id': blog.get('id'),
                'title': blog.get('title', {}).get('rendered', ''),
                'slug': blog.get('slug', ''),
                'old_url': blog.get('link', ''),
                'new_url': f"/blog/{blog.get('slug', '')}/",
            })
        
        # Save to CSV
        csv_file = self.output_dir / 'url_mapping.csv'
        if url_mappings:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=url_mappings[0].keys())
                writer.writeheader()
                writer.writerows(url_mappings)
            
            print(f"  💾 Saved {len(url_mappings)} URL mappings to {csv_file}")
        else:
            print("  ⚠️  No URLs to map")
    
    def print_summary(self):
        """Print extraction summary"""
        print("\n" + "=" * 60)
        print("✅ EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"\n📊 Content Summary:")
        print(f"   - Programs: {self.stats['programs']}")
        print(f"   - Funded Loans: {self.stats['funded_loans']}")
        print(f"   - Blog Posts: {self.stats['blogs']}")
        print(f"   - Media Files: {self.stats['media_files']}")
        print(f"   - Total Items: {sum([self.stats['programs'], self.stats['funded_loans'], self.stats['blogs']])}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.stats['errors']) > 5:
                print(f"   ... and {len(self.stats['errors']) - 5} more")
        
        print(f"\n📁 Output Files:")
        for file in sorted(self.output_dir.glob('*')):
            size = file.stat().st_size
            print(f"   - {file.name} ({size:,} bytes)")
        
        print(f"\n📝 Next Steps:")
        print(f"   1. Review extracted content in {self.output_dir}/")
        print(f"   2. Verify URL mappings in url_mapping.csv")
        print(f"   3. Run import_wordpress.py management command (Phase F.3)")
        print(f"   4. Verify content in Wagtail admin")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Extract content from WordPress for Wagtail migration'
    )
    parser.add_argument(
        '--base-url',
        default='http://localhost:8090',
        help='WordPress base URL (default: http://localhost:8090)'
    )
    parser.add_argument(
        '--output-dir',
        default='wp_export',
        help='Output directory for extracted content (default: wp_export)'
    )
    parser.add_argument(
        '--skip-media',
        action='store_true',
        help='Skip downloading media files'
    )
    
    parser.add_argument(
        '--per-page',
        type=int,
        default=20,
        help='Items per page (default: 20)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 60)
    print("WORDPRESS CONTENT EXTRACTOR")
    print("=" * 60)
    print(f"Source: {args.base_url}")
    print(f"Output: {args.output_dir}")
    print(f"Per Page: {args.per_page}")
    print(f"Timeout: {args.timeout}s")
    print("=" * 60)
    
    # Create extractor
    extractor = WordPressExtractor(args.base_url, args.output_dir, args.per_page, args.timeout)
    
    # Test connection
    print("\n🔌 Testing WordPress REST API connection...")
    try:
        response = extractor.session.get(f"{extractor.api_url}", timeout=10)
        response.raise_for_status()
        print("  ✅ Connected successfully")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        print("\nPlease ensure:")
        print("  1. WordPress is running")
        print("  2. REST API is accessible")
        print("  3. Base URL is correct")
        sys.exit(1)
    
    # Extract content
    programs = extractor.extract_programs()
    funded_loans = extractor.extract_funded_loans()
    blogs = extractor.extract_blogs()
    
    # Download media
    if not args.skip_media:
        extractor.download_media([programs, funded_loans, blogs])
    else:
        print("\n⏭️  Skipping media download")
    
    # Generate URL mapping
    extractor.generate_url_mapping(programs, funded_loans, blogs)
    
    # Print summary
    extractor.print_summary()


if __name__ == '__main__':
    main()
