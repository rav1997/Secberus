from django.conf.urls import url
from .views import Pull

urlpatterns = [
    url(r'^$', Pull.as_view(), name='aws-pull'),
]
