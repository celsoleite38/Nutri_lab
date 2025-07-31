from django.urls import path
from . import views
#from .views import consultas_json, CalendarioView
from .views import (CalendarioView, CriarAgendamentoView, detalhes_consulta, consultas_json, EditarConsultaView, cancelar_consulta_view)
app_name = 'agenda'

urlpatterns = [
    path('', CalendarioView.as_view(), name='calendario'),
    path('consultas/', consultas_json, name='consultas_json'),
    path('novo/', CriarAgendamentoView.as_view(), name='novo_agendamento'),
    path('consulta/<int:pk>/', detalhes_consulta, name='detalhes_consulta'),
    path("consulta/<int:pk>/editar/", EditarConsultaView.as_view(), name="editar_consulta"),
    path("consulta/<int:pk>/cancelar/", cancelar_consulta_view, name="cancelar_consulta"), # NOVA ROTA PARA CANCELAMENTO
]