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
    whatsapp = models.BooleanField(default=False, verbose_name="É WhatsApp?")
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
    peso = models.FloatField(null=True, blank=True)  # Ex: 99.99 kg
    altura = models.FloatField(null=True, blank=True)  # Ex: 1.99 m
    percentual_gordura = models.FloatField(null=True, blank=True)  # Ex: 25.50%
    percentual_musculo = models.FloatField(null=True, blank=True)  # Ex: 45.75%
    
    
    
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
            try:
                nutrientes = item.calcular_nutrientes()
                
                # Mapeamento flexível de chaves
                mapeamento_chaves = {
                    'energia': ['energia', 'calorias', 'kcal', 'energia_kcal'],
                    'proteina': ['proteina', 'proteinas', 'proteina_g'],
                    'carboidrato': ['carboidrato', 'carboidratos', 'carboidrato_g'],
                    'lipidios': ['lipidios', 'lipideos', 'gordura', 'gorduras', 'lipidios_g'],
                    'fibra': ['fibra', 'fibras', 'fibra_g']
                }
                
                for chave_destino, chaves_origem in mapeamento_chaves.items():
                    for chave_origem in chaves_origem:
                        if chave_origem in nutrientes:
                            total[chave_destino] += float(nutrientes[chave_origem] or 0)
                            break
                        
            except Exception as e:
                print(f"Erro ao calcular nutrientes do item {item}: {e}")
                continue
        
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
        
        try:
            for refeicao in self.refeicoes.all():
                nutrientes = refeicao.total_nutrientes()
                
                # Debug (remover depois)
                print(f"DEBUG - Refeição {refeicao.titulo}: {nutrientes}")
                
                for key in total:
                    valor = nutrientes.get(key, 0)
                    total[key] += float(valor) if valor else 0
                    
        except Exception as e:
            print(f"Erro ao calcular nutrientes do plano: {e}")
        
        # Debug final
        print(f"DEBUG - Total do plano: {total}")
        
        return total
    
    def duracao_dias(self):
        """Calcula a duração do plano em dias"""
        if self.data_inicio and self.data_fim:
            return (self.data_fim - self.data_inicio).days + 1  # +1 para incluir ambos os dias
        return 0