from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .users.views import UserViewSet, UserCreateViewSet, SendNewPhonenumberVerifyViewSet, DepositCreateViewSet, \
    WithdrawalCreateViewSet, P2PCreateViewSet, ListTransactionsViewSet, RetrieveTransactionViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)
router.register(r'phone', SendNewPhonenumberVerifyViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    #   path('jet_api/', include('jet_django.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/users/<str:user_id>/deposits', DepositCreateViewSet.as_view({'post': 'create'}), name="deposit-url"),
    path('api/v1/users/<str:user_id>/withdrawals', WithdrawalCreateViewSet.as_view({'post': 'create'}), name="withdrawal-url"),
    path('api/v1/account/<str:sender_account_id>/transfers/<str:recipient_account_id>', P2PCreateViewSet.as_view({'post': 'create'}), name="p2p-transfer-url"),
    path('api/v1/account/<str:account_id>/transactions', ListTransactionsViewSet.as_view({'get': 'list'}), name="user-transactions"),
    path('api/v1/account/transactions/<str:transaction_id>', RetrieveTransactionViewSet.as_view({'get': 'retrieve'}), name="user-transaction"),
    path('api-token-auth/', views.obtain_auth_token),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),


    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

