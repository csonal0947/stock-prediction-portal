from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import StockMetric
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from math import ceil
from django.db.models import Q

class StockListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Query params
        exchange = request.GET.get('exchange', '').upper()  # NSE, BSE or empty for both
        search = request.GET.get('search', '').strip()
        has_metrics = request.GET.get('has_metrics', '').strip().lower()
        try:
            page = int(request.GET.get('page', '1'))
        except ValueError:
            page = 1
        try:
            page_size = int(request.GET.get('page_size', '10'))
        except ValueError:
            page_size = 10
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10

        qs = StockMetric.objects.all()
        if exchange in ('NSE', 'BSE'):
            qs = qs.filter(exchange__iexact=exchange)

        if has_metrics in ('1', 'true', 'yes'):
            metric_q = (
                Q(eps__isnull=False)
                | Q(pe_ratio__isnull=False)
                | Q(roe__isnull=False)
                | Q(roa__isnull=False)
                | Q(roce__isnull=False)
                | Q(ev_to_ebitda__isnull=False)
            )
            qs = qs.filter(metric_q)

        if search:
            qs = qs.filter(symbol__icontains=search)

        total = qs.count()
        total_pages = ceil(total / page_size) if total > 0 else 1

        start = (page - 1) * page_size
        end = start + page_size

        stocks = list(qs.order_by('symbol').values(
            'symbol', 'exchange', 'current_price', 'market_cap',
            'eps', 'pe_ratio', 'last_updated'
        )[start:end])

        return Response({
            'stocks': stocks,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
            }
        })

class StockMetricView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, symbol):
        try:
            exchange = request.GET.get('exchange', '').strip().upper()
            qs = StockMetric.objects.filter(symbol=symbol.upper())
            if exchange:
                qs = qs.filter(exchange__iexact=exchange)

            stock = qs.order_by('exchange', '-last_updated').first()
            if not stock:
                raise StockMetric.DoesNotExist

            data = {
                'symbol': stock.symbol,
                'exchange': stock.exchange,
                'current_price': stock.current_price,
                'fifty_two_week_high': stock.fifty_two_week_high,
                'fifty_two_week_low': stock.fifty_two_week_low,
                'market_cap': stock.market_cap,
                'eps': stock.eps,
                'forward_eps': stock.forward_eps,
                'pe_ratio': stock.pe_ratio,
                'forward_pe': stock.forward_pe,
                'price_to_book': stock.price_to_book,
                'roe': stock.roe,
                'roa': stock.roa,
                'roce': stock.roce,
                'ev_to_ebitda': stock.ev_to_ebitda,
                'debt_to_equity': stock.debt_to_equity,
                'current_ratio': stock.current_ratio,
                'beta': stock.beta,
                'gross_margin': stock.gross_margin,
                'operating_margin': stock.operating_margin,
                'profit_margin': stock.profit_margin,
                'revenue_growth': stock.revenue_growth,
                'earnings_growth': stock.earnings_growth,
                'dividend_yield': stock.dividend_yield,
                'last_updated': stock.last_updated
            }
            return Response(data)
        except StockMetric.DoesNotExist:
            return Response(
                {'error': 'Stock not found'},
                status=status.HTTP_404_NOT_FOUND
            )
