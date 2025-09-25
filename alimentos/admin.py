# alimentos/admin.py

from django.contrib import admin
from .models import Alimento, CategoriaAlimento
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class CategoriaAlimentoResource(resources.ModelResource):
    class Meta:
        model = CategoriaAlimento
        fields = ('id', 'nome', 'descricao')

@admin.register(CategoriaAlimento)
class CategoriaAlimentoAdmin(ImportExportModelAdmin):
    resource_class = CategoriaAlimentoResource
    list_display = ['nome', 'descricao_curta']
    search_fields = ['nome']
    
    def descricao_curta(self, obj):
        return obj.descricao[:50] + '...' if obj.descricao and len(obj.descricao) > 50 else obj.descricao
    descricao_curta.short_description = 'Descrição'


class AlimentoResource(resources.ModelResource):
    class Meta:
        model = Alimento
        # Escolha os campos que você quer no seu CSV. É uma boa prática
        # incluir todos os campos que você preenche com frequência.
        fields = (
            'id', 'nome', 'categoria', 'energia_kcal', 'proteina_g', 
            'lipidios_g', 'carboidrato_g', 'fibra_alimentar_g', 'calcio_mg', 
            'ferro_mg', 'sodio_mg', 'vitamina_c_mg', 'medida_caseira', 
            'quantidade_medida_caseira', 'ativo', 'fonte'
        )

        skip_unchanged = True
        report_skipped = True


@admin.register(Alimento)
class AlimentoAdmin(ImportExportModelAdmin): # <<< MUDANÇA PRINCIPAL AQUI
    # 4. Associe a classe Resource que acabamos de criar
    resource_class = AlimentoResource

    # Todo o resto da sua configuração de admin pode continuar exatamente igual!
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

