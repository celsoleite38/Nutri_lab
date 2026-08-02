# nutri_lab/paginas_vendas/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Plano(models.Model): # Adicionado
    nome = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, unique=True, help_text="Usado na URL de checkout, ex: 1-mes")
    descricao = models.TextField(blank=True, help_text="Descrição do plano e/ou condições da promoção")
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duracao_dias = models.PositiveIntegerField(default=30, help_text="Duração da assinatura em dias")
    ativo = models.BooleanField(default=True, help_text="Exibir este plano na página de vendas")
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição (menor aparece primeiro)")
    eh_teste_gratis = models.BooleanField(default=False, help_text="Marca este como o plano de teste grátis")

    # Campos de promoção
    eh_promocional = models.BooleanField(default=False, help_text="Marca este plano como promocional")
    validade_promocao = models.DateTimeField(
        null=True, blank=True,
        help_text="Data/hora limite da promoção. Após essa data o plano não aparece mais (se promocional)."
    )

    class Meta:
        ordering = ['ordem', 'preco']
        verbose_name = "Plano"
        verbose_name_plural = "Planos"

    def __str__(self):
        return self.nome

    @property
    def promocao_valida(self):
        """Indica se a promoção ainda está dentro do prazo (ou não é promocional)."""
        if not self.eh_promocional:
            return True
        if not self.validade_promocao:
            return True
        return self.validade_promocao > timezone.now()

    @property
    def visivel(self):
        """Regra final: deve aparecer na página de vendas?"""
        return self.ativo and self.promocao_valida

class Assinatura(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assinaturas',) # Alterado on_delete
    email = models.EmailField()
    plano = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    validade = models.DateTimeField() # Alterado de DateField para DateTimeField
    status = models.CharField(max_length=20, choices=[
        ("ativo", "Ativo"),
        ("cancelado", "Cancelado"),
        ("expirado", "Expirado"),
        ("teste", "Teste Gratuito"),
        ("pendente", "Pendente"), # Adicionado
    ])
    data_pagamento = models.DateTimeField(auto_now_add=True)
    eh_teste_gratis = models.BooleanField(default=False)
    asaas_payment_id = models.CharField( # Adicionado
        max_length=100, blank=True, null=True
    )

    def __str__(self):
        return f"{self.email} - {self.plano} - {self.status}"

    @property
    def esta_ativo(self):
        """Verifica se a assinatura ainda é válida."""
        from django.utils import timezone
        return self.status in ("ativo", "teste") and self.validade > timezone.now()