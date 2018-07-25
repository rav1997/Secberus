from django.conf.urls import url, include
from .views import UserCreate, AccountActivate, LogOut, ForgetPasswordView, PasswordChangeView,ActivationEmailResend

urlpatterns = [
    url(r'^create/$', UserCreate.as_view(), name='create'),
    url(r'^logout/$', LogOut.as_view(), name='logout'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            AccountActivate.as_view(), name='activate'),
    url(r'^activate/resend/$',ActivationEmailResend.as_view(),name='activate-resend'),
    url(r'^password/reset/$', ForgetPasswordView.as_view(),
        name='forget_password'),
    url(r'^password/reset/confirm/$', PasswordChangeView.as_view(),
        name='password_reset_confirm'),
]
