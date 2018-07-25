from django.conf.urls import url
from .views import ListCompanies

urlpatterns = [
    url(r'^list$', ListCompanies.as_view(), name='list-companies'),
]
