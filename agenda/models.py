from datetime import datetime, timedelta # Adicionado timedelta
from django.db import models
from django.contrib.auth.models import User
from plataforma.models import Pacientes

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    data_nascimento = models.DateField()

    def __str__(self):
        return self.nome

class Consulta(models.Model):
    STATUS_CHOICES = [
        ("agendado", "Agendado"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
        ("realizado", "Realizado"),
    ]

    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    profissional = models.ForeignKey(User, on_delete=models.CASCADE)
    data_hora = models.DateTimeField("Data e Hora" )
    duracao = models.PositiveIntegerField("Duração (minutos)", default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="agendado")
    observacoes = models.TextField("Observações", blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def data_hora_fim(self):
        return self.data_hora + timedelta(minutes=self.duracao)

    class Meta:
        ordering = ["data_hora"]

    def __str__(self):
        return f"{self.paciente.nome} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
