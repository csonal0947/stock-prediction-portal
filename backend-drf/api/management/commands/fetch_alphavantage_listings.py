import csv
import requests
from io import StringIO
from django.core.management.base import BaseCommand
from decouple import config
from api.models import StockMetric

ALPHA_VANTAGE_API_KEY = config('ALPHA_VANTAGE_API_KEY')
ALPHA_LISTING_URL = 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'

class Command(BaseCommand):
    help = 'Fetch full listings from AlphaVantage LISTING_STATUS CSV and upsert symbols'

    def handle(self, *args, **options):
        if not ALPHA_VANTAGE_API_KEY:
            self.stdout.write(self.style.ERROR('ALPHA_VANTAGE_API_KEY not set in environment'))
            return

        url = ALPHA_LISTING_URL.format(api_key=ALPHA_VANTAGE_API_KEY)
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Failed to fetch listings: {resp.status_code}'))
            return

        # AlphaVantage returns CSV text
        text = resp.text
        f = StringIO(text)
        reader = csv.DictReader(f)

        total = 0
        created = 0
        updated = 0
        for row in reader:
            # Typical fields: symbol,name,exchange,assetType,ipoDate,delistingDate,status
            symbol = row.get('symbol') or row.get('Symbol')
            exchange = row.get('exchange') or row.get('exchangeCode') or row.get('Exchange') or 'UNKNOWN'
            if not symbol:
                continue
            total += 1
            exch = exchange.upper() if isinstance(exchange, str) else 'UNKNOWN'
            obj, was_created = StockMetric.objects.update_or_create(
                symbol=symbol.upper(),
                exchange=exch,
                defaults={}
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f'Total rows processed: {total}'))
        self.stdout.write(self.style.SUCCESS(f'Created: {created}, Updated: {updated}'))
