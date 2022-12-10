from django.urls import path


urlpatterns = [
    path('', ),
    path('<str:name>/', ),
    path('transactions/', ),
    path('transactions/<int:transaction_id>/', ),
    path('transactions/<str:wallet_name>/', ),
]
