from pathlib import Path
from ratesheets.ingestion.csv_reader import RateSheetCSVReader
csv_path = Path('../../Ratesheet List - Ratesheets.csv')
reader = RateSheetCSVReader(csv_path)
configs = reader.read_web_sources()
print(f'Found {len(configs)} web sources')
for c in configs[:3]:
    print(f'- {c.lender_name}: {c.url}')
