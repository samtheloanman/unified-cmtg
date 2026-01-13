from pathlib import Path
from ratesheets.ingestion.downloader import RateSheetDownloader
cache_dir = Path('./ratesheet_cache')
downloader = RateSheetDownloader(cache_dir)
# Test with Acra (public URL)
url = 'https://acralending.com/wp-content/uploads/2020/RateSheets/Wholesale/acra-ws-ratematrix-1stTDs.pdf'
path = downloader.download(url, 'Test Acra')
print(f'Downloaded: {path}')
downloader.close()
