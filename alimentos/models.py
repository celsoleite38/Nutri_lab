# alimentos/models.py
from django.db import models
from django.core.validators import MinValueValidator

class CategoriaAlimento(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria de Alimento'
        verbose_name_plural = 'Categorias de Alimentos'

    def __str__(self):
        return self.nome

class Alimento(models.Model):
    nome = models.CharField(max_length=200)
    nome_cientifico = models.CharField(max_length=200, blank=True)
    categoria = models.ForeignKey(CategoriaAlimento, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Informações nutricionais por 100g
    energia_kcal = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Energia (kcal)")
    proteina_g = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Proteína (g)")
    lipidios_g = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Lipídios (g)")
    carboidrato_g = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Carboidrato (g)")
    fibra_alimentar_g = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Fibra Alimentar (g)")
    calcio_mg = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Cálcio (mg)")
    ferro_mg = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Ferro (mg)")
    sodio_mg = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Sódio (mg)")
    vitamina_c_mg = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], default=0, verbose_name="Vitamina C (mg)")
    
    # Medidas caseiras
    medida_caseira = models.CharField(max_length=100, help_text="Ex: 1 colher de sopa, 1 unidade")
    quantidade_medida_caseira = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Quantidade da medida caseira (g)")
    
    # Controle
    ativo = models.BooleanField(default=True)
    fonte = models.CharField(max_length=200, default="TBCA - USP", verbose_name="Fonte dos dados")
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Alimento'
        verbose_name_plural = 'Alimentos'

    def __str__(self):
        return self.nome

    def calcular_nutrientes_por_porcao(self, quantidade_g):
        """Calcula os nutrientes para uma quantidade específica em gramas"""
        fator = quantidade_g / 100
        return {
            'energia': round(float(self.energia_kcal) * fator, 2),
            'proteina': round(float(self.proteina_g) * fator, 2),
            'lipidios': round(float(self.lipidios_g) * fator, 2),
            'carboidrato': round(float(self.carboidrato_g) * fator, 2),
            'fibra': round(float(self.fibra_alimentar_g) * fator, 2),
            'calcio_mg': round(float(self.calcio_mg) * fator, 2),
            'ferro_mg': round(float(self.ferro_mg) * fator, 2),
            'sodio_mg': round(float(self.sodio_mg) * fator, 2),
            'vitamina_c_mg': round(float(self.vitamina_c_mg) * fator, 2),
        }