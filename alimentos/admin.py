# alimentos/admin.py
from django.contrib import admin
from .models import Alimento, CategoriaAlimento

@admin.register(CategoriaAlimento)
class CategoriaAlimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao_curta']
    search_fields = ['nome']
    
    def descricao_curta(self, obj):
        return obj.descricao[:50] + '...' if obj.descricao and len(obj.descricao) > 50 else obj.descricao
    descricao_curta.short_description = 'Descrição'

@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'energia_kcal', 'proteina_g', 'carboidrato_g', 'ativo']
    list_filter = ['categoria', 'ativo']
    search_fields = ['nome', 'nome_cientifico']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'nome_cientifico', 'categoria', 'ativo')
        }),
        ('Informações Nutricionais (por 100g)', {
            'fields': (
                'energia_kcal', 'proteina_g', 'lipidios_g', 'carboidrato_g',
                'fibra_alimentar_g', 'calcio_mg', 'ferro_mg', 'sodio_mg', 'vitamina_c_mg'
            )
        }),
        ('Medida Caseira', {
            'fields': ('medida_caseira', 'quantidade_medida_caseira')
        }),
        ('Metadados', {
            'fields': ('fonte', 'data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['data_criacao', 'data_atualizacao']