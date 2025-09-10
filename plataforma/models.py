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
    
    def __str__(self):
        return self.nome
    
    def idade(self):
        if self.datanascimento:
            today = date.today()
            return today.year - self.datanascimento.year - ((today.month, today.day) < (self.datanascimento.month, self.datanascimento.day))
        return None

class DadosPaciente(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    data = models.DateTimeField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)  # Alterado para Decimal
    altura = models.DecimalField(max_digits=3, decimal_places=2)  # Alterado para Decimal
    percentual_gordura = models.DecimalField(max_digits=4, decimal_places=1)  # Alterado para Decimal
    percentual_musculo = models.DecimalField(max_digits=4, decimal_places=1)  # Alterado para Decimal
    colesterol_hdl = models.IntegerField()
    colesterol_ldl = models.IntegerField()
    colesterol_total = models.IntegerField()
    trigliceridios = models.IntegerField()
    
    def __str__(self):
        return f"Paciente({self.paciente.nome}, {self.peso})"
    
    def imc(self):
        if self.altura > 0:
            return self.peso / (self.altura ** 2)
        return 0

class Refeicao(models.Model):
    TIPO_CHOICES = (
        ('CAFE_MANHA', 'Café da Manhã'),
        ('LANCHE_MANHA', 'Lanche da Manhã'),
        ('ALMOCO', 'Almoço'),
        ('LANCHE_TARDE', 'Lanche da Tarde'),
        ('JANTAR', 'Jantar'),
        ('CEIA', 'Ceia'),
    )
    
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='ALMOCO')
    titulo = models.CharField(max_length=50)
    horario = models.TimeField()
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"
    
    def total_nutrientes(self):
        """Calcula o total de nutrientes da refeição"""
        total = {
            'energia': 0,
            'proteina': 0,
            'carboidrato': 0,
            'lipidios': 0,
            'fibra': 0
        }
        
        for item in self.itens.all():
            nutrientes = item.calcular_nutrientes()
            for key in total:
                total[key] += nutrientes.get(key, 0)
        
        return total

class ItemRefeicao(models.Model):
    refeicao = models.ForeignKey(Refeicao, on_delete=models.CASCADE, related_name='itens')
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
        return self.alimento.calcular_nutrientes_por_porcao(float(self.quantidade_g))

class PlanoAlimentar(models.Model):
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, default="Plano Alimentar")
    data_inicio = models.DateField()
    data_fim = models.DateField()
    objetivo = models.TextField(blank=True)
    refeicoes = models.ManyToManyField(Refeicao)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Plano de {self.paciente.nome} - {self.nome}"
    
    def total_nutrientes(self):
        """Calcula o total de nutrientes do plano"""
        total = {
            'energia': 0,
            'proteina': 0,
            'carboidrato': 0,
            'lipidios': 0,
            'fibra': 0
        }
        
        for refeicao in self.refeicoes.all():
            nutrientes = refeicao.total_nutrientes()
            for key in total:
                total[key] += nutrientes.get(key, 0)
        
        return total