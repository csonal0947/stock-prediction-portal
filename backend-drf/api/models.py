from django.db import models


class StockMetric(models.Model):
	symbol = models.CharField(max_length=20)
	# Exchange: NSE, BSE, NASDAQ, NYSE, etc. Default UNKNOWN to avoid migration issues.
	exchange = models.CharField(max_length=10, default='UNKNOWN')

	# Yahoo ticker mapping (e.g., RELIANCE.NS for NSE, TCS.BO for BSE)
	yahoo_ticker = models.CharField(max_length=32, null=True, blank=True)

	# Price
	current_price = models.FloatField(null=True, blank=True)
	fifty_two_week_high = models.FloatField(null=True, blank=True)
	fifty_two_week_low = models.FloatField(null=True, blank=True)

	# Core metrics
	eps = models.FloatField(null=True, blank=True)
	forward_eps = models.FloatField(null=True, blank=True)
	pe_ratio = models.FloatField(null=True, blank=True)
	forward_pe = models.FloatField(null=True, blank=True)
	price_to_book = models.FloatField(null=True, blank=True)
	roe = models.FloatField(null=True, blank=True)
	roa = models.FloatField(null=True, blank=True)
	roce = models.FloatField(null=True, blank=True)
	ev_to_ebitda = models.FloatField(null=True, blank=True)

	# Balance sheet & risk
	debt_to_equity = models.FloatField(null=True, blank=True)
	current_ratio = models.FloatField(null=True, blank=True)
	beta = models.FloatField(null=True, blank=True)

	# Margins & growth
	gross_margin = models.FloatField(null=True, blank=True)
	operating_margin = models.FloatField(null=True, blank=True)
	profit_margin = models.FloatField(null=True, blank=True)
	revenue_growth = models.FloatField(null=True, blank=True)
	earnings_growth = models.FloatField(null=True, blank=True)

	# Market
	market_cap = models.BigIntegerField(null=True, blank=True)
	dividend_yield = models.FloatField(null=True, blank=True)

	last_updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.symbol} ({self.exchange})"

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=['symbol', 'exchange'], name='uniq_symbol_exchange')
		]
