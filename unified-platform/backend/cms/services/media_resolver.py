"""
WordPress Media Resolver

Handles resolution of WordPress media URLs to local paths for import.
Extracts image references from HTML content and prepares them for Wagtail image import.
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


class MediaResolver:
    """
    Resolves WordPress media URLs to downloadable paths.

    Usage:
        resolver = MediaResolver('https://custommortgageinc.com')
        images = resolver.extract_images_from_html(html_content)
        for img in images:
            print(f"{img['alt']}: {img['src']}")
    """

    def __init__(self, wordpress_base_url: str):
        """
        Initialize resolver with WordPress site base URL.

        Args:
            wordpress_base_url: Base URL of WordPress site (e.g., https://custommortgageinc.com)
        """
        self.base_url = wordpress_base_url.rstrip('/')
        self.wp_content_pattern = re.compile(r'/wp-content/uploads/(\d{4}/\d{2}/[^"\'\s]+)')

    def extract_images_from_html(self, html: str) -> List[Dict[str, str]]:
        """
        Extract all image references from HTML content.

        Args:
            html: HTML content string

        Returns:
            List of dicts with image metadata:
            [
                {
                    'src': 'https://example.com/wp-content/uploads/2024/01/image.png',
                    'alt': 'Alt text',
                    'title': 'Title',
                    'local_path': 'wp-content/uploads/2024/01/image.png',
                    'filename': 'image.png'
                },
                ...
            ]
        """
        soup = BeautifulSoup(html, 'lxml')
        images = []

        for img_tag in soup.find_all('img'):
            src = img_tag.get('src', '')

            if not src:
                continue

            # Make absolute URL if relative
            if src.startswith('/'):
                src = urljoin(self.base_url, src)

            # Skip if not from WordPress uploads
            if 'wp-content/uploads' not in src:
                continue

            # Extract local path
            local_path = self._extract_local_path(src)

            if not local_path:
                continue

            images.append({
                'src': src,
                'alt': img_tag.get('alt', ''),
                'title': img_tag.get('title', ''),
                'local_path': local_path,
                'filename': os.path.basename(local_path),
                'width': img_tag.get('width'),
                'height': img_tag.get('height'),
            })

        return images

    def _extract_local_path(self, url: str) -> Optional[str]:
        """
        Extract local wp-content path from full URL.

        Args:
            url: Full image URL

        Returns:
            Relative path like 'wp-content/uploads/2024/01/image.png' or None
        """
        match = self.wp_content_pattern.search(url)

        if match:
            date_path_filename = match.group(1)  # e.g., '2024/01/image.png'
            return f'wp-content/uploads/{date_path_filename}'

        return None

    def resolve_srcset(self, srcset: str) -> List[Dict[str, any]]:
        """
        Parse WordPress srcset attribute to get all image sizes.

        Args:
            srcset: srcset attribute value (e.g., "image-300x200.jpg 300w, image-1024x768.jpg 1024w")

        Returns:
            List of dicts with URL, width, and local path for each size
        """
        images = []

        # Parse srcset format: "url 300w, url 1024w, ..."
        srcset_pattern = re.compile(r'([^\s,]+)\s+(\d+)w')

        for match in srcset_pattern.finditer(srcset):
            url = match.group(1)
            width = int(match.group(2))

            local_path = self._extract_local_path(url)

            if local_path:
                images.append({
                    'src': url,
                    'width': width,
                    'local_path': local_path,
                })

        return images

    def get_image_metadata_from_url(self, url: str) -> Dict[str, any]:
        """
        Extract metadata from WordPress image URL.

        Args:
            url: Image URL

        Returns:
            Dict with year, month, filename, extension, dimensions (if in filename)
        """
        metadata = {
            'url': url,
            'year': None,
            'month': None,
            'filename': None,
            'extension': None,
            'width': None,
            'height': None,
        }

        # Extract date from path
        date_match = re.search(r'/(\d{4})/(\d{2})/', url)
        if date_match:
            metadata['year'] = int(date_match.group(1))
            metadata['month'] = int(date_match.group(2))

        # Extract filename
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        metadata['filename'] = filename

        # Extract extension
        _, ext = os.path.splitext(filename)
        metadata['extension'] = ext.lstrip('.')

        # Try to extract dimensions from filename (e.g., image-1024x768.jpg)
        dim_match = re.search(r'-(\d+)x(\d+)\.', filename)
        if dim_match:
            metadata['width'] = int(dim_match.group(1))
            metadata['height'] = int(dim_match.group(2))

        return metadata

    def replace_images_in_html(
        self,
        html: str,
        replacement_map: Dict[str, str]
    ) -> str:
        """
        Replace WordPress image URLs with Wagtail image URLs.

        Args:
            html: Original HTML content
            replacement_map: Dict mapping old URLs to new Wagtail image URLs

        Returns:
            Updated HTML with replaced image URLs
        """
        soup = BeautifulSoup(html, 'lxml')

        for img_tag in soup.find_all('img'):
            old_src = img_tag.get('src', '')

            if old_src in replacement_map:
                img_tag['src'] = replacement_map[old_src]

                # Also update srcset if present
                if img_tag.get('srcset'):
                    # For now, remove srcset as we'd need all sizes mapped
                    del img_tag['srcset']

        return str(soup)


class MediaImporter:
    """
    Imports WordPress media into Wagtail.

    Coordinates with MediaResolver to download and import images.
    """

    def __init__(self, media_resolver: MediaResolver):
        """
        Initialize importer.

        Args:
            media_resolver: Configured MediaResolver instance
        """
        self.resolver = media_resolver

    def import_images_for_page(
        self,
        html: str,
        page_model
    ) -> Tuple[str, List]:
        """
        Import all images from HTML content into Wagtail.

        Args:
            html: HTML content containing images
            page_model: Wagtail Page model instance

        Returns:
            Tuple of (updated_html, list_of_wagtail_images)

        Note:
            This is a placeholder. Actual implementation will:
            1. Download images from WordPress
            2. Create Wagtail Image objects
            3. Replace URLs in HTML
            4. Return updated HTML
        """
        images = self.resolver.extract_images_from_html(html)

        # TODO: Implement actual download and import
        # For now, return original HTML and empty list
        return html, []

    def download_image(self, url: str, save_path: str) -> bool:
        """
        Download image from URL to local path.

        Args:
            url: Image URL to download
            save_path: Local filesystem path to save image

        Returns:
            True if successful, False otherwise

        Note:
            Placeholder - implement with requests.get() and file writing
        """
        # TODO: Implement download logic
        # import requests
        # response = requests.get(url, stream=True)
        # with open(save_path, 'wb') as f:
        #     for chunk in response.iter_content(chunk_size=8192):
        #         f.write(chunk)
        return False


# Example usage
if __name__ == '__main__':
    # Test the resolver
    resolver = MediaResolver('https://custommortgageinc.com')

    sample_html = '''
    <img src="https://custommortgageinc.com/wp-content/uploads/2024/01/sample-image.jpg" alt="Sample">
    <img src="/wp-content/uploads/2023/12/another-image-1024x768.png" alt="Another">
    '''

    images = resolver.extract_images_from_html(sample_html)

    print("Extracted images:")
    for img in images:
        print(f"  - {img['filename']}: {img['local_path']}")
