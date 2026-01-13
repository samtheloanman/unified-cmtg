import httpx
from pathlib import Path
from datetime import datetime
import hashlib
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RateSheetDownloader:
    """
    Download rate sheet PDFs from lender websites.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; RateSheetBot/1.0)'
            }
        )

    def download(
        self,
        url: str,
        lender_name: str,
        password: Optional[str] = None
    ) -> Optional[Path]:
        """
        Download a rate sheet PDF.
        """
        try:
            # Basic Auth if password provided
            auth = None
            if password:
                auth = (lender_name.lower().replace(' ', ''), password)

            logger.info(f"Downloading {lender_name} from {url}...")
            response = self.client.get(url, auth=auth)
            response.raise_for_status()

            # Generate filename
            date_str = datetime.now().strftime('%Y-%m-%d')
            safe_name = lender_name.lower().replace(' ', '_')
            filename = f"{safe_name}_{date_str}.pdf"
            filepath = self.cache_dir / filename

            # Check hash to avoid duplicates
            content_hash = hashlib.md5(response.content).hexdigest()
            hash_file = filepath.with_suffix('.hash')

            if hash_file.exists() and filepath.exists():
                existing_hash = hash_file.read_text().strip()
                if existing_hash == content_hash:
                    logger.info(f"No changes for {lender_name}")
                    return filepath

            # Save
            filepath.write_bytes(response.content)
            hash_file.write_text(content_hash)

            logger.info(f"Saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            print(f"Error downloading {lender_name}: {e}")
            return None

    def close(self):
        self.client.close()
