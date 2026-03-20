import csv
import requests
from io import StringIO
from django.core.management.base import BaseCommand
from decouple import config
from api.models import StockMetric

NSE_URL_DEFAULT = 'https://archives.nseindia.com/content/equities/EQUITY_L.csv'
BSE_URL_ENV = 'BSE_LIST_URL'  # optional env var to set a CSV URL for BSE listings

class Command(BaseCommand):
    help = 'Fetch NSE and BSE listings and upsert symbols with exchange field'

    def add_arguments(self, parser):
        parser.add_argument('--only-nse', action='store_true', help='Only fetch NSE list')
        parser.add_argument('--only-bse', action='store_true', help='Only fetch BSE list')

    def handle(self, *args, **options):
        only_nse = options.get('only_nse')
        only_bse = options.get('only_bse')

        if not only_bse:
            self.fetch_nse()
        if not only_nse:
            self.fetch_bse()

    def fetch_nse(self):
        url = NSE_URL_DEFAULT
        headers = {'User-Agent': 'Mozilla/5.0'}
        self.stdout.write(self.style.NOTICE(f'Fetching NSE list from {url}'))
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to download NSE list: {e}'))
            return

        f = StringIO(resp.text)
        reader = csv.DictReader(f)
        total = created = updated = 0
        for row in reader:
            symbol = (row.get('SYMBOL') or row.get('Symbol') or '').strip()
            if not symbol:
                continue
            total += 1
            obj, was_created = StockMetric.objects.update_or_create(
                symbol=symbol.upper(),
                exchange='NSE',
                defaults={}
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'NSE: Processed {total}; Created {created}; Updated {updated}'))

    def fetch_bse(self):
        bse_url = config(BSE_URL_ENV, default='')
        if not bse_url:
            self.stdout.write(self.style.WARNING('BSE URL not configured via env var BSE_LIST_URL; attempting common fallback'))
            # Common fallback isn't guaranteed; user can set BSE_LIST_URL in .env
            # Try a few well-known endpoints (best-effort)
            candidates = [
                'https://www.bseindia.com/download/BhavCopy/Equity/EQ_ISINCODE.csv',
                'https://www.bseindia.com/static/json/Equity.csv',
            ]
        else:
            candidates = [bse_url]

        headers = {'User-Agent': 'Mozilla/5.0'}
        total = created = updated = 0
        succeeded = False
        for url in candidates:
            self.stdout.write(self.style.NOTICE(f'Trying BSE source: {url}'))
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                resp.raise_for_status()
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to fetch {url}: {e}'))
                continue

            # Try to parse CSV; columns vary across sources
            f = StringIO(resp.text)
            try:
                reader = csv.DictReader(f)
                for row in reader:
                    # Try common field names
                    symbol = (row.get('SC_CODE') or row.get('SC_NAME') or row.get('SCRIP') or row.get('symbol') or '')
                    # Some BSE CSVs have ISIN and security codes; skip non-symbol rows
                    if not symbol:
                        continue
                    symbol = str(symbol).strip()
                    # Many BSE tickers on Yahoo use .BO suffix; store symbol without suffix
                    total += 1
                    obj, was_created = StockMetric.objects.update_or_create(
                        symbol=symbol.upper(),
                        exchange='BSE',
                        defaults={}
                    )
                    if was_created:
                        created += 1
                    else:
                        updated += 1
                succeeded = True
                break
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error parsing CSV from {url}: {e}'))
                continue

        if not succeeded:
            self.stdout.write(self.style.ERROR('Failed to fetch/parse any BSE listing. Set BSE_LIST_URL in your .env to a CSV URL and retry.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'BSE: Processed {total}; Created {created}; Updated {updated}'))
