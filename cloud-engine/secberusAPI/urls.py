"""secberusAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

from .views import *

schema_view = get_swagger_view(title='Secberus API')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^users/', include('secberus.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', CustomObtainJSONWebToken.as_view(), name='login'),
    url(r'^aws/', include('aws.urls')),
    url(r'^docs/$', schema_view),
    url(r'^pull/', include('puller.urls')),
    url(r'^company/', include('company.urls')),
    url(r'^countryList/$',CountryListView.as_view(), name='country-list'),
    url(r'^stateList/(?P<countryCode>[A-Za-z]+)/$',StateListView.as_view(), name='state-list'),
    url(r'^security-policy/', include('securityPolicy.urls')),
]
