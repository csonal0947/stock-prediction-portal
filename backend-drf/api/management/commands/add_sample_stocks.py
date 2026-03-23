from django.core.management.base import BaseCommand
from api.models import StockMetric

class Command(BaseCommand):
    help = 'Add sample stock data for testing'

    def handle(self, *args, **options):
        sample_stocks = [
            # ── NASDAQ ──────────────────────────────────────────────────────
            {
                'symbol': 'AAPL', 'exchange': 'NASDAQ',
                'current_price': 213.49, 'eps': 7.91, 'pe_ratio': 32.14,
                'roe': 1.52, 'roa': 0.244, 'roce': None, 'ev_to_ebitda': 25.3,
                'market_cap': 3.26e12,
            },
            {
                'symbol': 'MSFT', 'exchange': 'NASDAQ',
                'current_price': 415.32, 'eps': 11.86, 'pe_ratio': 35.8,
                'roe': 0.48, 'roa': 0.198, 'roce': None, 'ev_to_ebitda': 22.1,
                'market_cap': 3.08e12,
            },
            {
                'symbol': 'GOOGL', 'exchange': 'NASDAQ',
                'current_price': 165.78, 'eps': 6.25, 'pe_ratio': 26.5,
                'roe': 0.29, 'roa': 0.165, 'roce': None, 'ev_to_ebitda': 18.7,
                'market_cap': 2.04e12,
            },
            {
                'symbol': 'TSLA', 'exchange': 'NASDAQ',
                'current_price': 245.89, 'eps': 3.62, 'pe_ratio': 67.8,
                'roe': 0.31, 'roa': 0.112, 'roce': None, 'ev_to_ebitda': 45.2,
                'market_cap': 7.83e11,
            },
            {
                'symbol': 'AMZN', 'exchange': 'NASDAQ',
                'current_price': 174.60, 'eps': 2.98, 'pe_ratio': 58.4,
                'roe': 0.21, 'roa': 0.078, 'roce': None, 'ev_to_ebitda': 34.6,
                'market_cap': 1.82e12,
            },
            # ── NSE (Indian stocks – Yahoo suffix .NS) ───────────────────────
            {
                'symbol': 'RELIANCE', 'exchange': 'NSE',
                'current_price': 2820.50, 'eps': 100.34, 'pe_ratio': 28.1,
                'roe': 0.146, 'roa': 0.081, 'roce': 0.112, 'ev_to_ebitda': 12.4,
                'market_cap': 1.91e13,
            },
            {
                'symbol': 'TCS', 'exchange': 'NSE',
                'current_price': 3912.10, 'eps': 124.20, 'pe_ratio': 31.5,
                'roe': 0.524, 'roa': 0.376, 'roce': 0.652, 'ev_to_ebitda': 24.8,
                'market_cap': 1.42e13,
            },
            {
                'symbol': 'HDFCBANK', 'exchange': 'NSE',
                'current_price': 1668.40, 'eps': 84.57, 'pe_ratio': 19.7,
                'roe': 0.168, 'roa': 0.019, 'roce': None, 'ev_to_ebitda': 14.9,
                'market_cap': 1.27e13,
            },
            {
                'symbol': 'INFY', 'exchange': 'NSE',
                'current_price': 1754.25, 'eps': 67.88, 'pe_ratio': 25.8,
                'roe': 0.328, 'roa': 0.228, 'roce': 0.408, 'ev_to_ebitda': 18.2,
                'market_cap': 7.29e12,
            },
            {
                'symbol': 'ICICIBANK', 'exchange': 'NSE',
                'current_price': 1248.70, 'eps': 65.22, 'pe_ratio': 19.1,
                'roe': 0.178, 'roa': 0.021, 'roce': None, 'ev_to_ebitda': 13.7,
                'market_cap': 8.79e12,
            },
            {
                'symbol': 'BHARTIARTL', 'exchange': 'NSE',
                'current_price': 1598.30, 'eps': 40.15, 'pe_ratio': 39.8,
                'roe': 0.453, 'roa': 0.072, 'roce': 0.089, 'ev_to_ebitda': 11.8,
                'market_cap': 9.54e12,
            },
            {
                'symbol': 'WIPRO', 'exchange': 'NSE',
                'current_price': 482.55, 'eps': 22.38, 'pe_ratio': 21.6,
                'roe': 0.178, 'roa': 0.122, 'roce': 0.218, 'ev_to_ebitda': 14.1,
                'market_cap': 2.51e12,
            },
            {
                'symbol': 'SBIN', 'exchange': 'NSE',
                'current_price': 794.80, 'eps': 76.24, 'pe_ratio': 10.4,
                'roe': 0.192, 'roa': 0.018, 'roce': None, 'ev_to_ebitda': 8.2,
                'market_cap': 7.09e12,
            },
            {
                'symbol': 'LT', 'exchange': 'NSE',
                'current_price': 3622.60, 'eps': 115.42, 'pe_ratio': 31.4,
                'roe': 0.152, 'roa': 0.034, 'roce': 0.178, 'ev_to_ebitda': 19.6,
                'market_cap': 5.10e12,
            },
            {
                'symbol': 'KOTAKBANK', 'exchange': 'NSE',
                'current_price': 1823.45, 'eps': 90.31, 'pe_ratio': 20.2,
                'roe': 0.153, 'roa': 0.022, 'roce': None, 'ev_to_ebitda': 15.8,
                'market_cap': 3.63e12,
            },
            {
                'symbol': 'HINDUNILVR', 'exchange': 'NSE',
                'current_price': 2398.75, 'eps': 42.14, 'pe_ratio': 56.9,
                'roe': 1.002, 'roa': 0.245, 'roce': 1.312, 'ev_to_ebitda': 42.1,
                'market_cap': 5.63e12,
            },
            {
                'symbol': 'BAJFINANCE', 'exchange': 'NSE',
                'current_price': 6845.20, 'eps': 145.38, 'pe_ratio': 47.1,
                'roe': 0.222, 'roa': 0.042, 'roce': None, 'ev_to_ebitda': 29.8,
                'market_cap': 4.22e12,
            },
            {
                'symbol': 'MARUTI', 'exchange': 'NSE',
                'current_price': 10978.50, 'eps': 490.25, 'pe_ratio': 22.4,
                'roe': 0.172, 'roa': 0.102, 'roce': 0.208, 'ev_to_ebitda': 15.9,
                'market_cap': 3.32e12,
            },
            {
                'symbol': 'SUNPHARMA', 'exchange': 'NSE',
                'current_price': 1804.30, 'eps': 70.12, 'pe_ratio': 25.7,
                'roe': 0.168, 'roa': 0.118, 'roce': 0.192, 'ev_to_ebitda': 19.8,
                'market_cap': 4.32e12,
            },
            # ── BSE (Indian stocks – Yahoo suffix .BO) ───────────────────────
            {
                'symbol': 'RELIANCE', 'exchange': 'BSE',
                'current_price': 2819.80, 'eps': 100.34, 'pe_ratio': 28.1,
                'roe': 0.146, 'roa': 0.081, 'roce': 0.112, 'ev_to_ebitda': 12.4,
                'market_cap': 1.91e13,
            },
            {
                'symbol': 'TCS', 'exchange': 'BSE',
                'current_price': 3910.55, 'eps': 124.20, 'pe_ratio': 31.5,
                'roe': 0.524, 'roa': 0.376, 'roce': 0.652, 'ev_to_ebitda': 24.8,
                'market_cap': 1.42e13,
            },
            {
                'symbol': 'HDFCBANK', 'exchange': 'BSE',
                'current_price': 1667.90, 'eps': 84.57, 'pe_ratio': 19.7,
                'roe': 0.168, 'roa': 0.019, 'roce': None, 'ev_to_ebitda': 14.9,
                'market_cap': 1.27e13,
            },
            {
                'symbol': 'INFY', 'exchange': 'BSE',
                'current_price': 1753.40, 'eps': 67.88, 'pe_ratio': 25.8,
                'roe': 0.328, 'roa': 0.228, 'roce': 0.408, 'ev_to_ebitda': 18.2,
                'market_cap': 7.29e12,
            },
            {
                'symbol': 'TATASTEEL', 'exchange': 'BSE',
                'current_price': 158.45, 'eps': 18.24, 'pe_ratio': 8.7,
                'roe': 0.118, 'roa': 0.048, 'roce': 0.094, 'ev_to_ebitda': 6.8,
                'market_cap': 1.98e12,
            },
            {
                'symbol': 'POWERGRID', 'exchange': 'BSE',
                'current_price': 321.60, 'eps': 20.38, 'pe_ratio': 15.8,
                'roe': 0.214, 'roa': 0.056, 'roce': 0.098, 'ev_to_ebitda': 9.4,
                'market_cap': 2.99e12,
            },
            {
                'symbol': 'NTPC', 'exchange': 'BSE',
                'current_price': 348.20, 'eps': 18.42, 'pe_ratio': 18.9,
                'roe': 0.126, 'roa': 0.044, 'roce': 0.088, 'ev_to_ebitda': 10.2,
                'market_cap': 3.38e12,
            },
            {
                'symbol': 'ONGC', 'exchange': 'BSE',
                'current_price': 272.35, 'eps': 30.18, 'pe_ratio': 9.0,
                'roe': 0.148, 'roa': 0.074, 'roce': 0.118, 'ev_to_ebitda': 4.8,
                'market_cap': 3.42e12,
            },
            {
                'symbol': 'COALINDIA', 'exchange': 'BSE',
                'current_price': 448.70, 'eps': 60.24, 'pe_ratio': 7.5,
                'roe': 0.524, 'roa': 0.342, 'roce': 0.648, 'ev_to_ebitda': 5.2,
                'market_cap': 2.76e12,
            },
            {
                'symbol': 'TITAN', 'exchange': 'BSE',
                'current_price': 3412.80, 'eps': 68.45, 'pe_ratio': 49.8,
                'roe': 0.302, 'roa': 0.148, 'roce': 0.378, 'ev_to_ebitda': 38.4,
                'market_cap': 3.03e12,
            },
            {
                'symbol': 'JSWSTEEL', 'exchange': 'BSE',
                'current_price': 948.60, 'eps': 50.12, 'pe_ratio': 18.9,
                'roe': 0.168, 'roa': 0.068, 'roce': 0.138, 'ev_to_ebitda': 9.6,
                'market_cap': 2.30e12,
            },
        ]

        for stock_data in sample_stocks:
            stock, created = StockMetric.objects.update_or_create(
                symbol=stock_data['symbol'],
                exchange=stock_data['exchange'],
                defaults={
                    'current_price': stock_data.get('current_price'),
                    'market_cap': stock_data.get('market_cap'),
                    'eps': stock_data['eps'],
                    'pe_ratio': stock_data['pe_ratio'],
                    'roe': stock_data['roe'],
                    'roa': stock_data['roa'],
                    'roce': stock_data['roce'],
                    'ev_to_ebitda': stock_data['ev_to_ebitda'],
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(self.style.SUCCESS(f'{status}: {stock.symbol}'))

        self.stdout.write(self.style.SUCCESS(f'\nTotal stocks in database: {StockMetric.objects.count()}'))
