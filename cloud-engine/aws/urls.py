from django.conf.urls import url
from .views import SaveCredential, ScheduleIntervalSetting, EditIntervalSetting\
, GetExternalId, ListAccounts

urlpatterns = [
    url(r'^create/$', SaveCredential.as_view(), name='aws-create'),
    url(r'^scheduler/$', ScheduleIntervalSetting.as_view(), name='scheduler-setting'),
    url(r'^scheduler/edit/$', EditIntervalSetting.as_view(), name='scheduler-setting-edit'),
    url(r'^get/external_id$', GetExternalId.as_view(), name='get-external-id'),
    url(r'^list$', ListAccounts.as_view(), name='list-accounts'),
]
