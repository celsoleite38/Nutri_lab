from django.contrib import admin
from .models import Assinatura, Plano


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):

    list_display = (
        'nome',
        'slug',
        'preco',
        'duracao_dias',
        'ativo',
        'eh_promocional',
        'validade_promocao',
        'ordem',
        'visivel',
    )

    list_filter = (
        'ativo',
        'eh_promocional',
        'eh_teste_gratis',
    )

    search_fields = ('nome', 'slug', 'descricao')

    list_editable = ('ativo', 'ordem')

    ordering = ('ordem', 'preco')

    fieldsets = (
        ('Informações do Plano', {
            'fields': ('nome', 'slug', 'descricao', 'preco', 'duracao_dias')
        }),
        ('Exibição', {
            'fields': ('ativo', 'ordem', 'eh_teste_gratis')
        }),
        ('Promoção', {
            'fields': ('eh_promocional', 'validade_promocao'),
            'description': 'Marque "eh_promocional" e defina uma data de validade para criar uma '
                            'oferta por tempo limitado. Após a validade, o plano deixa de aparecer '
                            'automaticamente na página de vendas. Use o campo Descrição para '
                            'explicar as condições da promoção (ex: "válido para novos clientes, '
                            'cobrança recorrente no valor normal após o período promocional").'
        }),
    )

    @admin.display(boolean=True, description='Visível na página')
    def visivel(self, obj):
        return obj.visivel


@admin.register(Assinatura)
class AssinaturaAdmin(admin.ModelAdmin):

    list_display = (
        'email',
        'plano',
        'valor',
        'status',
        'eh_teste_gratis',
        'validade',
        'data_pagamento',
        'asaas_payment_id',
    )

    list_filter = (
        'status',
        'plano',
        'eh_teste_gratis',
    )

    search_fields = (
        'email',
        'plano',
        'asaas_payment_id',
    )

    ordering = ('-data_pagamento',)

    readonly_fields = (
        'data_pagamento',
        'asaas_payment_id',
    )

    actions = ['marcar_ativo', 'marcar_cancelado']

    @admin.action(description='✅ Marcar selecionadas como ATIVO')
    def marcar_ativo(self, request, queryset):
        atualizadas = queryset.update(status='ativo')
        self.message_user(request, f'{atualizadas} assinatura(s) marcadas como ativas.')

    @admin.action(description='❌ Marcar selecionadas como CANCELADO')
    def marcar_cancelado(self, request, queryset):
        atualizadas = queryset.update(status='cancelado')
        self.message_user(request, f'{atualizadas} assinatura(s) canceladas.')
