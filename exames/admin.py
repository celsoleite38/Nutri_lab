from django.contrib import admin
from .models import TipoExame, SolicitacaoExame, ResultadoExame
from import_export import resources
from import_export.admin import ImportExportModelAdmin


class TipoExameResource(resources.ModelResource):
    class Meta:
        model = TipoExame
        fields = ('id', 'nome', 'unidade_padrao', 'ref_min', 'ref_max')

class TipoExameAdmin(ImportExportModelAdmin):
    resource_class = TipoExameResource

    list_display = ('nome', 'unidade_padrao', 'ref_min', 'ref_max')
    search_fields = ('nome',)

admin.site.register(TipoExame, TipoExameAdmin)

#admin.site.register(TipoExame)
admin.site.register(SolicitacaoExame)
admin.site.register(ResultadoExame)
