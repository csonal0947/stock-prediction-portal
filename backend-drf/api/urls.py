from django.urls import path
from accounts import views as UserViews
from . import views as ApiViews
from .views_currency_proxy import currency_rates, market_data
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns= [
    path('register/', UserViews.RegisterView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('stocks/', ApiViews.StockListView.as_view(), name='stock_list'),
    path('stocks/<str:symbol>/', ApiViews.StockMetricView.as_view(), name='stock_detail'),
    path('currency-proxy/', currency_rates, name='currency_proxy'),
    path('market-data/', market_data, name='market_data'),
]