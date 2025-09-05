from django.db import models
from django.contrib.auth.models import User
from alimentos.models import Alimento

class Pacientes(models.Model):
    choices_sexo = (('Feminino', 'Feminino'),
                    ('Masculino', 'Masculino'),
                    ('Outros', 'Outros'))
    choices_estadocivil = (('Casado(a)', 'Casado(a)'),
                    ('Solteiro(a)', 'Solteiro(a)'),
                    ('Divorciado(a)', 'Divorciado(a)'),
                    ('Viuvo(a)', 'Viuvo(a)'))
    nome = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14, verbose_name="CPF", blank=False, null=True)
    sexo = models.CharField(max_length=24, choices=choices_sexo)
    estadocivil = models.CharField(max_length=25, choices=choices_estadocivil)
    datanascimento = models.DateField(null=True, blank=True)
    naturalidade = models.CharField(max_length=120)
    profissao = models.CharField(max_length=50)
    email = models.EmailField()
    telefone = models.CharField(max_length=25)
    endereco = models.CharField(max_length=50, null=True)
    nutri = models.ForeignKey(User, on_delete=models.CASCADE)
                                                    #pode ser usar SET_NULL para quando apagar o fisio nao apague os pacientes dele
    def __str__(self):
        return self.nome
    

class DadosPaciente(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data = models.DateTimeField()
    peso = models.IntegerField()
    altura = models.IntegerField()
    percentual_gordura = models.IntegerField()
    percentual_musculo = models.IntegerField()
    colesterol_hdl = models.IntegerField()
    colesterol_ldl = models.IntegerField()
    colesterol_total = models.IntegerField()
    trigliceridios = models.IntegerField()
    
    def __str__(self):
        return f"Paciente({self.paciente.nome}, {self.peso})"
    
class Refeicao(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=50)
    horario = models.TimeField()
    carboidratos = models.IntegerField()
    proteinas = models.IntegerField()
    gorduras = models.IntegerField()
    
    def __str__(self):
        return self.titulo
    
class Opcao(models.Model):
    refeicao = models.ForeignKey(Refeicao, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to="Opcao/", blank=True, null=True)
    descricao = models.TextField()
    
    def __str__(self):
        return self.descricao
    

class ItemRefeicao(models.Model):
    refeicao = models.ForeignKey('Refeicao', on_delete=models.CASCADE)
    alimento = models.ForeignKey(Alimento, on_delete=models.CASCADE)
    quantidade_g = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Item de Refeição'
        verbose_name_plural = 'Itens de Refeição'

    def __str__(self):
        return f"{self.quantidade_g}g de {self.alimento.nome}"

    def calcular_nutrientes(self):
        """Calcula os nutrientes totais deste item"""
        return self.alimento.calcular_nutrientes_por_porcao(self.quantidade_g)