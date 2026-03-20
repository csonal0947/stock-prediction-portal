from django.core.management.base import BaseCommand
from api.models import StockMetric

class Command(BaseCommand):
    help = 'Add sample stock data for testing'

    def handle(self, *args, **options):
        sample_stocks = [
            {
                'symbol': 'AAPL',
                'exchange': 'NASDAQ',
                'eps': 7.91,
                'pe_ratio': 32.14,
                'roe': 1.52,
                'roa': 0.244,
                'roce': None,
                'ev_to_ebitda': 25.3
            },
            {
                'symbol': 'MSFT',
                'exchange': 'NASDAQ',
                'eps': 11.86,
                'pe_ratio': 35.8,
                'roe': 0.48,
                'roa': 0.198,
                'roce': None,
                'ev_to_ebitda': 22.1
            },
            {
                'symbol': 'GOOGL',
                'exchange': 'NASDAQ',
                'eps': 6.25,
                'pe_ratio': 26.5,
                'roe': 0.29,
                'roa': 0.165,
                'roce': None,
                'ev_to_ebitda': 18.7
            },
            {
                'symbol': 'TSLA',
                'exchange': 'NASDAQ',
                'eps': 3.62,
                'pe_ratio': 67.8,
                'roe': 0.31,
                'roa': 0.112,
                'roce': None,
                'ev_to_ebitda': 45.2
            },
            {
                'symbol': 'AMZN',
                'exchange': 'NASDAQ',
                'eps': 2.98,
                'pe_ratio': 58.4,
                'roe': 0.21,
                'roa': 0.078,
                'roce': None,
                'ev_to_ebitda': 34.6
            },
        ]

        for stock_data in sample_stocks:
            stock, created = StockMetric.objects.update_or_create(
                symbol=stock_data['symbol'],
                exchange=stock_data['exchange'],
                defaults={
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
