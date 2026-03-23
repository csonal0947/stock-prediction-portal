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
        # BSE official JSON API – returns all active equity scrips
        BSE_JSON_API = 'https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&industry=&segment=Equity&status=Active'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bseindia.com/',
        }
        self.stdout.write(self.style.NOTICE(f'Fetching BSE list from BSE JSON API'))
        try:
            resp = requests.get(BSE_JSON_API, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError('Unexpected BSE JSON response format')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'BSE JSON API failed: {e}'))
            # Fallback: also check env var
            bse_url = config(BSE_URL_ENV, default='')
            if not bse_url:
                self.stdout.write(self.style.ERROR('Set BSE_LIST_URL env var to a CSV URL as fallback.'))
                return
            self.stdout.write(self.style.NOTICE(f'Trying BSE_LIST_URL fallback: {bse_url}'))
            try:
                resp = requests.get(bse_url, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json() if bse_url.endswith('.json') else None
                if data is None:
                    f = StringIO(resp.text)
                    data = [
                        {'scrip_id': (row.get('SC_CODE') or row.get('SYMBOL') or row.get('scrip_id') or '')}
                        for row in csv.DictReader(f)
                    ]
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f'Fallback also failed: {e2}'))
                return

        total = created = updated = 0
        for row in data:
            # The official API uses 'scrip_id' as the ticker symbol
            symbol = (row.get('scrip_id') or row.get('SYMBOL') or row.get('SC_CODE') or '').strip()
            if not symbol or symbol.isdigit():
                continue
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

        self.stdout.write(self.style.SUCCESS(f'BSE: Processed {total}; Created {created}; Updated {updated}'))
