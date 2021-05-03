from django.urls import path, include

from .views import AccountList, AccountDetail, LedgerList, LedgerDetail

urlpatterns = [
    path('<int:pk>/', AccountDetail.as_view()),
    path('', AccountList.as_view()),
    path('ledger/<int:pk>/', LedgerDetail.as_view()),
    path('ledger/', LedgerList.as_view()),
    path('api-auth/', include('rest_framework.urls')),
]