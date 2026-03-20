import requests
import time
from django.core.management.base import BaseCommand
from api.models import StockMetric
from decouple import config

ALPHA_VANTAGE_API_KEY = config('ALPHA_VANTAGE_API_KEY')  # Add your AlphaVantage API key to your .env file
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'

# Example: symbols = ['AAPL', 'MSFT', 'GOOGL']
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL']  # You can expand this list

class Command(BaseCommand):
    help = 'Fetch stock metrics from AlphaVantage API and update the database.'

    def handle(self, *args, **options):
        for index, symbol in enumerate(SYMBOLS):
            # Add delay between requests (AlphaVantage free tier: 25 requests/day, 5 requests/minute)
            if index > 0:
                self.stdout.write(f"Waiting 15 seconds before next request...")
                time.sleep(15)  # Wait 15 seconds between requests to avoid rate limit
            
            # AlphaVantage OVERVIEW endpoint provides comprehensive company data
            url = f"{ALPHA_VANTAGE_BASE_URL}?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # Check if data is valid (AlphaVantage returns error messages in the response)
                if data and 'Symbol' in data:
                    # Parse the EV/EBITDA ratio - AlphaVantage provides it as EVToEBITDA
                    ev_to_ebitda = None
                    if 'EVToEBITDA' in data and data['EVToEBITDA'] != 'None':
                        try:
                            ev_to_ebitda = float(data['EVToEBITDA'])
                        except (ValueError, TypeError):
                            ev_to_ebitda = None
                    
                    StockMetric.objects.update_or_create(
                        symbol=symbol,
                        exchange='NASDAQ',
                        defaults={
                            'eps': float(data.get('EPS', 0)) if data.get('EPS') and data.get('EPS') != 'None' else None,
                            'pe_ratio': float(data.get('PERatio', 0)) if data.get('PERatio') and data.get('PERatio') != 'None' else None,
                            'roe': float(data.get('ReturnOnEquityTTM', 0)) if data.get('ReturnOnEquityTTM') and data.get('ReturnOnEquityTTM') != 'None' else None,
                            'roa': float(data.get('ReturnOnAssetsTTM', 0)) if data.get('ReturnOnAssetsTTM') and data.get('ReturnOnAssetsTTM') != 'None' else None,
                            'roce': None,  # AlphaVantage doesn't provide ROCE directly
                            'ev_to_ebitda': ev_to_ebitda,
                        }
                    )
                    self.stdout.write(self.style.SUCCESS(f"Updated {symbol}"))
                else:
                    error_msg = data.get('Error Message', data.get('Note', 'No data'))
                    self.stdout.write(self.style.WARNING(f"No data for {symbol}: {error_msg}"))
            else:
                self.stdout.write(self.style.ERROR(f"Failed to fetch {symbol}: {response.status_code}"))
