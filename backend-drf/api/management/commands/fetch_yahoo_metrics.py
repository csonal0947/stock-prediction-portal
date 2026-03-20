import time
import re
from django.core.management.base import BaseCommand
from api.models import StockMetric

try:
    import yfinance as yf
except Exception:
    yf = None

class Command(BaseCommand):
    help = 'Fetch live metrics from Yahoo Finance (yfinance) for mapped tickers and update StockMetric.'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0, help='Limit number of tickers to process (0 = all)')
        parser.add_argument('--sleep', type=float, default=0.5, help='Seconds to sleep between requests')
        parser.add_argument('--verify-only', action='store_true', help='Only verify existing metrics; do not overwrite non-null fields')
        parser.add_argument(
            '--exchanges',
            type=str,
            default='BSE,NSE',
            help='Comma-separated exchange filter (default: BSE,NSE). Use ALL for no exchange filter.',
        )

    @staticmethod
    def _clean_symbol(symbol):
        if not symbol:
            return ''
        value = symbol.strip().upper()
        # Keep common Yahoo-compatible chars
        return re.sub(r'[^A-Z0-9\.-]', '', value)

    def _preferred_ticker(self, stock):
        exch = (stock.exchange or '').upper().strip()
        clean_symbol = self._clean_symbol(stock.symbol)
        mapped = (stock.yahoo_ticker or '').strip().upper()

        if exch == 'NSE' and clean_symbol:
            return f'{clean_symbol}.NS'
        if exch == 'BSE' and clean_symbol:
            return f'{clean_symbol}.BO'

        # Fallback to mapped ticker for non-Indian exchanges only when explicitly requested
        if mapped and re.fullmatch(r'[A-Z0-9\.\-]+', mapped):
            return mapped
        return ''

    def handle(self, *args, **options):
        if yf is None:
            self.stdout.write(self.style.ERROR('yfinance is not installed. Please install yfinance and retry.'))
            return

        limit = options.get('limit') or 0
        sleep_seconds = options.get('sleep') or 0.5
        verify_only = options.get('verify_only')
        exchanges_raw = (options.get('exchanges') or 'BSE,NSE').strip()

        if exchanges_raw.upper() == 'ALL':
            allowed_exchanges = None
        else:
            allowed_exchanges = [x.strip().upper() for x in exchanges_raw.split(',') if x.strip()]

        qs = StockMetric.objects.exclude(yahoo_ticker__isnull=True).exclude(yahoo_ticker__exact='')
        if allowed_exchanges:
            qs = qs.filter(exchange__in=allowed_exchanges)
        qs = qs.order_by('id')
        total_qs = qs.count()
        if limit > 0:
            qs = qs[:limit]

        processed = 0
        updated = 0
        skipped = 0
        errors = 0

        for stock in qs:
            processed += 1
            ticker = self._preferred_ticker(stock)
            if not ticker:
                skipped += 1
                continue

            try:
                t = yf.Ticker(ticker)
                info = t.info or {}

                def to_float(v):
                    try:
                        return float(v) if v is not None else None
                    except Exception:
                        return None

                def to_int(v):
                    try:
                        return int(v) if v is not None else None
                    except Exception:
                        return None

                # Build candidate updates
                candidates = {
                    'current_price':      to_float(info.get('currentPrice') or info.get('regularMarketPrice')),
                    'fifty_two_week_high':to_float(info.get('fiftyTwoWeekHigh')),
                    'fifty_two_week_low': to_float(info.get('fiftyTwoWeekLow')),
                    'eps':                to_float(info.get('trailingEps')),
                    'forward_eps':        to_float(info.get('forwardEps')),
                    'pe_ratio':           to_float(info.get('trailingPE')),
                    'forward_pe':         to_float(info.get('forwardPE')),
                    'price_to_book':      to_float(info.get('priceToBook')),
                    'roe':                to_float(info.get('returnOnEquity')),
                    'roa':                to_float(info.get('returnOnAssets')),
                    'ev_to_ebitda':       to_float(info.get('enterpriseToEbitda')),
                    'debt_to_equity':     to_float(info.get('debtToEquity')),
                    'current_ratio':      to_float(info.get('currentRatio')),
                    'beta':               to_float(info.get('beta')),
                    'gross_margin':       to_float(info.get('grossMargins')),
                    'operating_margin':   to_float(info.get('operatingMargins')),
                    'profit_margin':      to_float(info.get('profitMargins')),
                    'revenue_growth':     to_float(info.get('revenueGrowth')),
                    'earnings_growth':    to_float(info.get('earningsGrowth')),
                    'market_cap':         to_int(info.get('marketCap')),
                    'dividend_yield':     to_float(info.get('dividendYield')),
                }

                updates = {}
                for field, value in candidates.items():
                    if value is None:
                        continue
                    # In verify_only mode skip fields already set
                    if verify_only and getattr(stock, field) is not None:
                        continue
                    updates[field] = value

                if not updates:
                    skipped += 1
                else:
                    if stock.yahoo_ticker != ticker:
                        updates['yahoo_ticker'] = ticker
                    for k, v in updates.items():
                        setattr(stock, k, v)
                    stock.save()
                    updated += 1

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.WARNING(f'Error fetching {ticker}: {e}'))

            if processed % 100 == 0:
                self.stdout.write(
                    f'Progress: {processed} processed | {updated} updated | {skipped} skipped | {errors} errors'
                )

            # Sleep between requests to be polite
            time.sleep(sleep_seconds)

        self.stdout.write(self.style.SUCCESS(f'Done. Processed: {processed}; Updated: {updated}; Skipped: {skipped}; Errors: {errors}; Total available: {total_qs}'))
