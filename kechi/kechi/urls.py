from django.conf.urls import include, url
from django.contrib import admin

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    # Examples:
    # url(r'^$', 'kechi.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^skate/', include('skate.urls')),
    url('^', include('django.contrib.auth.urls'))
]
urlpatterns += staticfiles_urlpatterns()
