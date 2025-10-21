from django.urls import path
from . import views

app_name = 'plataforma'

urlpatterns = [
    path('pacientes/', views.pacientes, name='pacientes'),
    path('dados_paciente/', views.dados_paciente_listar, name="dados_paciente_listar"),
    path('dados_paciente/<str:id>/', views.dados_paciente, name="dados_paciente"),
    path('editar_paciente/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('imprimir_paciente/<int:id>/', views.imprimir_paciente, name='imprimir_paciente'),
    path('grafico_peso/<str:id>/', views.grafico_peso, name="grafico_peso"),
    path('plano_alimentar_listar/', views.plano_alimentar_listar, name="plano_alimentar_listar"),
    path('plano_alimentar/<str:id>/', views.plano_alimentar, name="plano_alimentar"),
    path('refeicao/<str:id_paciente>/', views.refeicao, name="refeicao"),
    path('paciente/<int:paciente_id>/imprimir/', views.imprimir_opcao, name='imprimir_opcao'),
    path('opcao/<str:id_paciente>/', views.opcao, name="Opcao"),
    path('pacientes/<int:id>/', views.imprimir_dados_paciente, name='imprimir_dados_paciente'),
    
    
    
    path('plano/criar/<int:paciente_id>/', views.criar_plano_alimentar, name='criar_plano_alimentar'),
    path('plano/<int:plano_id>/', views.detalhes_plano_alimentar, name='detalhes_plano_alimentar'),
    path('refeicao/adicionar/<int:paciente_id>/', views.adicionar_refeicao, name='adicionar_refeicao'),
    path('refeicao/editar/<int:refeicao_id>/', views.editar_refeicao, name='editar_refeicao'),
    path('refeicao/item/remover/<int:item_id>/', views.remover_item_refeicao, name='remover_item_refeicao'),
    path('api/buscar-alimentos-refeicao/', views.buscar_alimentos_refeicao, name='buscar_alimentos_refeicao'),
    path('api/calcular-nutrientes-item/', views.calcular_nutrientes_item, name='calcular_nutrientes_item'),
    path('plano/<int:plano_id>/remover-refeicao/<int:refeicao_id>/', views.remover_refeicao_plano, name='remover_refeicao_plano'),
    path('refeicao/remover/<int:refeicao_id>/', views.remover_refeicao, name='remover_refeicao'),
    
    path('plano/<int:plano_id>/desativar/', views.desativar_plano, name='desativar_plano'),
    path('plano/<int:plano_id>/reativar/', views.reativar_plano, name='reativar_plano'),
    
    path('plano/<int:plano_id>/adicionar-refeicao/', views.adicionar_refeicao_existente, name='adicionar_refeicao_existente'),
    
    path('paciente/<int:paciente_id>/copiar-plano/', views.copiar_plano_alimentar, name='copiar_plano_alimentar'),
    
    
    path('paciente/<int:paciente_id>/planos/', views.detalhes_paciente_planos, name='detalhes_paciente_planos'),
    path('paciente/<int:paciente_id>/criar-plano/', views.criar_plano_alimentar, name='criar_plano_alimentar'),
]