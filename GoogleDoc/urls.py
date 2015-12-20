from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = [
	url(r'^docEditor/', include('docEditor.urls')),
    url(r'^login/', include('login.urls', namespace="login")),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
]
