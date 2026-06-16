from django.contrib import admin
from .models import Consulta

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'profissional', 'data_hora', 'status')  # Corrigido para data_hora
    list_filter = ('status', 'profissional')
    date_hierarchy = 'data_hora'  # Corrigido para data_hora
    search_fields = ('paciente__nome', 'profissional__username')
    ordering = ('-data_hora',)
