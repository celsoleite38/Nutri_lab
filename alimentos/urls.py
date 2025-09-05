# alimentos/urls.py
from django.urls import path
from . import views

app_name = 'alimentos'

urlpatterns = [
    path('', views.lista_alimentos, name='lista_alimentos'),
    path('detalhe/<int:alimento_id>/', views.detalhe_alimento, name='detalhe_alimento'),
    path('adicionar/', views.adicionar_alimento, name='adicionar_alimento'),
    path('editar/<int:alimento_id>/', views.editar_alimento, name='editar_alimento'),
    path('buscar-ajax/', views.buscar_alimentos_ajax, name='buscar_alimentos_ajax'),
    path('calcular-nutrientes/', views.calcular_nutrientes, name='calcular_nutrientes'),
    
    # Categorias
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/adicionar/', views.adicionar_categoria, name='adicionar_categoria'),
    
    path('dashboard/', views.dashboard_nutricional, name='dashboard'),
    path('api/buscar/', views.buscar_alimentos_ajax, name='api_buscar'),
]