import re
import csv
import requests
from io import StringIO
from django.core.management.base import BaseCommand
from decouple import config
from api.models import StockMetric

BSE_PAGE_URL_ENV = 'BSE_LIST_URL'

class Command(BaseCommand):
    help = 'Scrape BSE list page for CSV links or extract symbols directly and upsert with exchange=BSE'

    def add_arguments(self, parser):
        parser.add_argument('--url', help='BSE scrips page URL (defaults to BSE_LIST_URL in .env)')

    def handle(self, *args, **options):
        url = options.get('url') or config(BSE_PAGE_URL_ENV, default='')
        if not url:
            self.stdout.write(self.style.ERROR('No URL provided and BSE_LIST_URL not set.'))
            return

        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to download page: {e}'))
            return

        html = resp.text
        # Look for CSV links in hrefs
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
        csv_links = []
        for href in hrefs:
            if href.lower().endswith('.csv') or 'csv' in href.lower():
                # Make absolute if needed
                if href.startswith('http'):
                    csv_links.append(href)
                else:
                    # resolve relative
                    if url.endswith('/'):
                        csv_links.append(url.rstrip('/') + '/' + href.lstrip('/'))
                    else:
                        base = url.rsplit('/', 1)[0]
                        csv_links.append(base + '/' + href.lstrip('/'))

        if csv_links:
            self.stdout.write(self.style.NOTICE(f'Found {len(csv_links)} candidate CSV links; trying first...'))
            csv_url = csv_links[0]
            try:
                r = requests.get(csv_url, headers=headers, timeout=30)
                r.raise_for_status()
                f = StringIO(r.text)
                reader = csv.DictReader(f)
                total = created = updated = 0
                for row in reader:
                    # try common symbol fields
                    symbol = (row.get('SC_CODE') or row.get('SC_NAME') or row.get('SCRIP') or row.get('symbol') or row.get('Symbol') or '')
                    if not symbol:
                        # try first col
                        first = next(iter(row.values()), '')
                        symbol = first
                    symbol = str(symbol).strip()
                    if not symbol:
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
                self.stdout.write(self.style.SUCCESS(f'CSV import succeeded: processed {total}; created {created}; updated {updated}'))
                return
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to download/parse CSV {csv_url}: {e}'))
                # fall through to HTML extraction

        # Fallback: extract symbol-like tokens from HTML using regex
        # BSE symbols often are uppercase words/numbers; we'll extract candidates using a conservative regex
        candidates = set()
        # common patterns: ticker code in table cells, e.g., >TCS< or >500325<; capture tokens of 2-8 uppercase letters/digits
        for match in re.findall(r'>([A-Z0-9.&-]{2,8})<', html):
            # filter out common words that are not tickers
            if match.isdigit() and len(match) < 4:
                # likely numeric codes, skip
                continue
            candidates.add(match)

        # If none found, try words inside table rows
        if not candidates:
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, flags=re.IGNORECASE | re.DOTALL)
            for r in rows:
                text = re.sub(r'<[^>]+>', ' ', r)
                for token in text.split():
                    t = token.strip().strip('(),')
                    if re.fullmatch(r'[A-Z0-9.&-]{2,8}', t):
                        candidates.add(t)

        if not candidates:
            self.stdout.write(self.style.ERROR('No candidate symbols found in HTML. Manual CSV URL required.'))
            return

        total = created = updated = 0
        for symbol in sorted(candidates):
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
        self.stdout.write(self.style.SUCCESS(f'HTML heuristic import: processed {total}; created {created}; updated {updated}'))
