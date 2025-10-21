from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('autenticacao.urls')),
    path('', RedirectView.as_view(url='/auth/logar/', permanent=False)),
    path('plataforma/', include('plataforma.urls', namespace='plataforma')),
    path('agenda/', include('agenda.urls',namespace='agenda')),
    path("alimentos/", include("alimentos.urls")),
    path('exames/', include('exames.urls', namespace='exames')),
    #path('', include('paginas_vendas.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)