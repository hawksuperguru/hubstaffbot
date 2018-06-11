from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from bot import urls as boturls

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^hubbot/', include('bot.urls')),
]