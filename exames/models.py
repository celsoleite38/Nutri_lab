from django.db import models
from plataforma.models import Pacientes
from django.core.exceptions import ValidationError
from decimal import Decimal

# Modelo para cadastrar os tipos de exames que o sistema conhece
class TipoExame(models.Model):
   
    nome = models.CharField(max_length=100, unique=True, help_text="Nome padronizado do exame, ex: 'Glicemia de Jejum'")
    unidade_padrao = models.CharField(max_length=20, help_text="Unidade de medida padrão, ex: 'mg/dL'")
    
   
    ref_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor de referência mínimo")
    ref_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Valor de referência máximo")
    unidade_padrao = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return self.nome

# Modelo para a solicitação em si
class SolicitacaoExame(models.Model):
    """
    Representa o "pedido de exames" feito em uma data para um paciente.
    Funciona como um contêiner para os resultados.
    """
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('C', 'Concluído'),
        ('A', 'Analisado'),
    ]
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE, related_name="solicitacoes_exames")
    data_solicitacao = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido de {self.paciente.nome} em {self.data_solicitacao.strftime('%d/%m/%Y')}"


class ResultadoExame(models.Model):
    
    solicitacao = models.ForeignKey(SolicitacaoExame, on_delete=models.CASCADE, related_name="resultados")
    tipo_exame = models.ForeignKey(TipoExame, on_delete=models.PROTECT)
    resultado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    pre_diagnostico_ia = models.TextField(blank=True, null=True, editable=False)

    class Meta:
        unique_together = ('solicitacao', 'tipo_exame')

    def save(self, *args, **kwargs):
        # A IA só deve rodar se houver um resultado.
        if self.resultado is not None:
            self.pre_diagnostico_ia = self.gerar_pre_diagnostico_simples()
        else:
            self.pre_diagnostico_ia = "Aguardando resultado." # Mensagem padrão
        super().save(*args, **kwargs)

    def gerar_pre_diagnostico_simples(self):
        if self.resultado is None:
            return "Aguardando resultado."
            
        ref_min = self.tipo_exame.ref_min
        ref_max = self.tipo_exame.ref_max
        
        if ref_min is None or ref_max is None:
            return "Valores de referência não cadastrados. Análise manual necessária."
        
        # Garantir que todos os valores sejam Decimal para comparação
        try:
            resultado_decimal = Decimal(str(self.resultado))
            ref_min_decimal = Decimal(str(ref_min))
            ref_max_decimal = Decimal(str(ref_max))
            
            if resultado_decimal < ref_min_decimal:
                return f"Atenção: Resultado ABAIXO do valor de referência ({ref_min} - {ref_max} {self.tipo_exame.unidade_padrao})."
            elif resultado_decimal > ref_max_decimal:
                return f"Atenção: Resultado ACIMA do valor de referência ({ref_min} - {ref_max} {self.tipo_exame.unidade_padrao})."
            else:
                return f"Resultado DENTRO do valor de referência ({ref_min} - {ref_max} {self.tipo_exame.unidade_padrao})."
                
        except (ValueError, TypeError):
            return "Erro na análise do resultado. Verifique os valores."


