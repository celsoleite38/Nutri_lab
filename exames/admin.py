from django.contrib import admin
from .models import TipoExame, SolicitacaoExame, ResultadoExame

admin.site.register(TipoExame)
admin.site.register(SolicitacaoExame)
admin.site.register(ResultadoExame)
