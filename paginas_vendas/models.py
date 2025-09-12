from django.db import models

class Assinatura(models.Model):
    email = models.EmailField()
    plano = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    validade = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ("ativo", "Ativo"),
        ("cancelado", "Cancelado"),
        ("expirado", "Expirado"),
        ("teste", "Teste Gratuito")
    ])
    data_pagamento = models.DateTimeField(auto_now_add=True)
    eh_teste_gratis = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.plano} - {self.status}"
