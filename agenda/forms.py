from django import forms
from django.core.exceptions import ValidationError, FieldError
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, DateTimeField # Importações para cálculo na query

from .models import Consulta
from plataforma.models import Pacientes # Importa o modelo Pacientes do app plataforma

class AgendamentoForm(forms.ModelForm):
    paciente = forms.ModelChoiceField(
        queryset=Pacientes.objects.none(), 
        label="Paciente", 
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Consulta
        fields = ["paciente", "data_hora", "duracao", "observacoes"]
        widgets = {
            "data_hora": forms.DateTimeInput(attrs={
                "type": "datetime-local",
                "class": "form-control"
            }, format="%Y-%m-%dT%H:%M"),
            "duracao": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 5,
                "step": 5
            }),
            "observacoes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            try:
                pacientes_do_usuario = Pacientes.objects.filter(nutri=self.user)
                self.fields["paciente"].queryset = pacientes_do_usuario
                if not pacientes_do_usuario.exists():
                    self.fields["paciente"].help_text = "Nenhum paciente cadastrado por você encontrado."
                else:
                    self.fields["paciente"].help_text = ""
            except FieldError:
                print(f"AVISO: Campo 'fisio' não encontrado no modelo Pacientes. A lista de pacientes não será filtrada.")
                self.fields["paciente"].queryset = Pacientes.objects.none()
                self.fields["paciente"].help_text = "Erro ao filtrar pacientes."
            except Exception as e:
                print(f"Erro inesperado ao filtrar pacientes: {e}")
                self.fields["paciente"].queryset = Pacientes.objects.none()
                self.fields["paciente"].help_text = "Erro inesperado ao carregar pacientes."
        else:
            self.fields["paciente"].queryset = Pacientes.objects.none()
            self.fields["paciente"].help_text = "Usuário não identificado."

    def clean(self):
        cleaned_data = super().clean()
        data_hora_nova = cleaned_data.get("data_hora")
        duracao_nova = cleaned_data.get("duracao")
        profissional = self.user

        if not profissional:
            raise ValidationError("Usuário profissional não identificado.")

        if data_hora_nova and duracao_nova:
            data_hora_fim_nova = data_hora_nova + timedelta(minutes=duracao_nova)

            # Consultas que podem conflitar para o mesmo profissional
            qs = Consulta.objects.filter(profissional=profissional)

            # Se estiver editando, exclua a própria consulta da verificação
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            
            # Adiciona um campo calculado 'data_hora_fim_existente' à queryset
            # Este cálculo é feito no banco de dados
            # Nota: F('duracao') é em minutos, então precisamos converter para timedelta
            # A forma mais direta de adicionar timedelta na query é um pouco complexa dependendo do DB.
            # Uma abordagem mais simples é filtrar grosseiramente e depois refinar em Python.

            # Filtro inicial para reduzir o número de consultas a serem verificadas em Python:
            # Pega consultas que terminam após o início da nova ou começam antes do fim da nova.
            consultas_potenciais = qs.filter(
                data_hora__lt=data_hora_fim_nova # Consulta existente começa antes do fim da nova
            ).filter(
                # E a consulta existente termina depois do início da nova.
                # Para isso, precisamos calcular o fim da existente. Vamos fazer isso em Python.
                data_hora__gte=data_hora_nova - timedelta(hours=4) # Otimização: não pegar consultas muito antigas
            )
            
            conflito_encontrado = False
            for consulta_existente in consultas_potenciais:
                # Calcula o fim da consulta existente
                data_hora_fim_existente = consulta_existente.data_hora + timedelta(minutes=consulta_existente.duracao)
                
                # Verifica a sobreposição:
                # (InícioA < FimB) e (FimA > InícioB)
                if (data_hora_nova < data_hora_fim_existente and 
                    data_hora_fim_nova > consulta_existente.data_hora):
                    conflito_encontrado = True
                    break
            
            if conflito_encontrado:
                raise ValidationError(
                    {"__all__": "Não permitido para este horário. Já existe uma consulta agendada."}, 
                    code="conflito_horario"
                )
        return cleaned_data

