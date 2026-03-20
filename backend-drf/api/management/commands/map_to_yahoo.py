from django.core.management.base import BaseCommand
from api.models import StockMetric

class Command(BaseCommand):
    help = 'Map NSE/BSE symbols to Yahoo tickers (.NS for NSE, .BO for BSE) and update StockMetric.yahoo_ticker'

    def add_arguments(self, parser):
        parser.add_argument('--verify', action='store_true', help='(Optional) verify tickers via yfinance if installed')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of rows to process (0 = all)')

    def handle(self, *args, **options):
        verify = options.get('verify')
        limit = options.get('limit') or 0

        qs = StockMetric.objects.all().order_by('id')
        if limit > 0:
            qs = qs[:limit]

        total = 0
        updated = 0
        skipped = 0

        yf = None
        if verify:
            try:
                import yfinance as yf_module
                yf = yf_module
            except Exception as e:
                self.stdout.write(self.style.WARNING('yfinance not available; skipping verification'))
                yf = None

        for stock in qs:
            total += 1
            symbol = stock.symbol
            if not symbol:
                skipped += 1
                continue

            # If yahoo_ticker already set and not empty, skip
            if stock.yahoo_ticker:
                skipped += 1
                continue

            yahoo = None
            exch = (stock.exchange or '').upper()
            if exch == 'NSE':
                yahoo = f"{symbol}.NS"
            elif exch == 'BSE':
                yahoo = f"{symbol}.BO"
            else:
                # default preferences: if symbol looks numeric, skip; else try .NS
                if symbol.isalpha():
                    yahoo = f"{symbol}.NS"
                else:
                    yahoo = f"{symbol}"

            # if yahoo already contains suffix, keep as is
            if yahoo.endswith('.NS') or yahoo.endswith('.BO') or yahoo.endswith('.NSX'):
                pass

            # Optional verification via yfinance: check if ticker info exists
            if yf:
                try:
                    t = yf.Ticker(yahoo)
                    info = t.info
                    # if no longName or regularMarketPrice available, try alternate suffix
                    if not info or (not info.get('regularMarketPrice') and not info.get('symbol')):
                        # try alternate suffix
                        if yahoo.endswith('.NS'):
                            alt = yahoo.replace('.NS', '.BO')
                        elif yahoo.endswith('.BO'):
                            alt = yahoo.replace('.BO', '.NS')
                        else:
                            alt = yahoo + '.NS'
                        t2 = yf.Ticker(alt)
                        info2 = t2.info
                        if info2 and (info2.get('regularMarketPrice') or info2.get('symbol')):
                            yahoo = alt
                except Exception:
                    # ignore verification errors
                    pass

            stock.yahoo_ticker = yahoo
            stock.save(update_fields=['yahoo_ticker'])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f'Processed: {total}; Updated: {updated}; Skipped: {skipped}'))
