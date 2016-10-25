from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from chm import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'upload$', views.upload, name='upload')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
