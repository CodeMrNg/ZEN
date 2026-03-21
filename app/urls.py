from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('language/', views.set_language_view, name='set-language'),
    path('login/', views.TradingLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('transactions/', views.transactions_view, name='transactions'),
    path('outils/', views.tools_view, name='tools'),
    path('parametres/', views.settings_view, name='settings'),
    path('api/dashboard/', views.dashboard_data_view, name='dashboard-data'),
    path('api/transactions/', views.transactions_data_view, name='transactions-data'),
    path('api/accounts/switch/', views.switch_account_view, name='account-switch'),
    path('api/trades/', views.create_trade_view, name='trade-create'),
    path('api/trades/<int:trade_id>/update/', views.update_trade_view, name='trade-update'),
    path('api/capital-movements/', views.create_capital_movement_view, name='capital-movement-create'),
    path('api/demo/', views.seed_demo_data_view, name='demo-seed'),
]
