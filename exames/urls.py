# exames/urls.py

from django.urls import path
from . import views

app_name = 'exames'

urlpatterns = [
   
    path('paciente/<int:paciente_id>/', views.listar_solicitacoes, name='listar_solicitacoes'),
    path('nova_solicitacao/<int:paciente_id>/', views.nova_solicitacao, name='nova_solicitacao'),
    path('solicitacao/<int:solicitacao_id>/', views.detalhe_solicitacao, name='detalhe_solicitacao'),
    path('imprimir/<int:solicitacao_id>/', views.imprimir_solicitacao, name='imprimir_solicitacao'),
]
