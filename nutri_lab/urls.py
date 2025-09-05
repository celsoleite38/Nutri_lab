from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/' , include('autenticacao.urls')),
    path('' , include('plataforma.urls')),
    path('agenda/', include('agenda.urls',namespace='agenda')),
    path("alimentos/", include("alimentos.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)