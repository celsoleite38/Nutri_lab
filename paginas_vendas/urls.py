from django.urls import path
from paginas_vendas import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.pagina_vendas, name='pagina_vendas'),
    path('pagamento/<str:plano_slug>/', views.checkout, name='checkout'),
    path('obrigado/', views.pagina_obrigado, name='pagina_obrigado'),
    path('webhook/asaas/', views.webhook_asaas, name='webhook_asaas'),
    path('dashboard/assinaturas/', views.dashboard_assinaturas, name='dashboard_assinaturas'),
    path('teste-gratis/', views.teste_gratis, name='teste_gratis'),
    path('teste-gratis/sucesso/', TemplateView.as_view(
        template_name='paginas_vendas/teste_gratis_sucesso.html'
    ), name='teste_gratis_sucesso'),
    path('recursos/', views.recursos, name='recursos'),
]
