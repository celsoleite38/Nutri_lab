from django.db import models
from django.contrib.auth.models import User

class Ativacao(models.Model):
    token = models.CharField(max_length=64)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ativo = models.BooleanField(default=False)
    email = models.EmailField(max_length=254, default='example@example.com')
    
    def __str__(self):
        return self.user.username
    
    #perfil profissional
class PerfilProfissional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_completo = models.CharField(max_length=101)
    cpf = models.CharField(max_length=14)
    cfn = models.CharField(max_length=20)
    nomeclinica = models.CharField(max_length=101, null=True)
    logotipo = models.ImageField(upload_to='media/logos_profissionais/', blank=True, null=True)

    def __str__(self):
        return self.nome_completo
    
