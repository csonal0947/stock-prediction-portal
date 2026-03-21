"""
URL configuration for stock_prediction_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'StockLens API is running',
        'endpoints': {
            'register': '/api/v1/register/',
            'login': '/api/v1/token/',
            'token_refresh': '/api/v1/token/refresh/',
            'stocks': '/api/v1/stocks/',
            'market_data': '/api/v1/market-data/',
            'currency_proxy': '/api/v1/currency-proxy/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),

    #Base API Endpoint
    path('api/v1/', include('api.urls'))
]
