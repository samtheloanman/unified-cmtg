import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class LenderRateSheetConfig:
    """Configuration for a lender's rate sheet source."""
    lender_name: str
    url: str
    program_type: str
    requires_auth: bool = False
    password: Optional[str] = None
    is_emailed: bool = False

class RateSheetCSVReader:
    """
    Read lender rate sheet configuration from CSV.
    """

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path

    def read_all(self) -> List[LenderRateSheetConfig]:
        """Read all lender configurations."""
        configs = []

        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found at {self.csv_path}")

        with open(self.csv_path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Handle potential whitespace in keys if CSV is messy
                row = {k.strip(): v for k, v in row.items() if k}

                # Check for required columns
                if 'Lender' not in row:
                    continue

                config = LenderRateSheetConfig(
                    lender_name=row.get('Lender', '').strip(),
                    url=row.get('Ratesheet Link', '').strip(),
                    program_type=row.get('Type', '').strip(),
                    requires_auth=row.get('PW', 'none').lower() not in ('none', '', 'n/a'),
                    password=row.get('PW') if row.get('PW', 'none').lower() not in ('none', '', 'n/a') else None,
                    is_emailed=row.get('Emailed', 'N').upper() == 'Y',
                )
                configs.append(config)

        return configs

    def read_web_sources(self) -> List[LenderRateSheetConfig]:
        """Get only lenders with web-based rate sheets."""
        return [c for c in self.read_all() if not c.is_emailed and c.url]
