from django.db import models
from django.contrib.auth.models import User
#from .models import Ativacao, PerfilProfissional, AlteracaoEmail

class Ativacao(models.Model):
    token = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Alterado de DO_NOTHING para CASCADE
    ativo = models.BooleanField(default=False)
    email = models.EmailField(max_length=254, default='example@example.com')

    def __str__(self):
        return self.user.username

#perfil profissional
class PerfilProfissional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=101)
    cpf = models.CharField(max_length=14)
    cfn = models.CharField(max_length=20) # Manter cfn para nutricionista
    nomeclinica = models.CharField(max_length=101, null=True)
    logotipo = models.ImageField(upload_to='logos_profissionais/', blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True) # Adicionado
    whatsapp = models.BooleanField(default=False) # Adicionado
    pode_excluir_evolucoes = models.BooleanField(default=False, verbose_name='Pode excluir evoluções') # Adicionado
    asaas_customer_id = models.CharField(max_length=100, blank=True, null=True) # Adicionado

    def __str__(self):
        return self.nome_completo

class AlteracaoEmail(models.Model): # Adicionado
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='alteracao_email')
    novo_email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} -> {self.novo_email}"