from django import forms
from .models import PerfilProfissional


class PerfilProfissionalForm(forms.ModelForm):
    class Meta:
        model = PerfilProfissional
        fields = ['nome_completo', 'cpf', 'cfn', 'nomeclinica', 'logotipo']
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'cfn': forms.TextInput(attrs={'class': 'form-control'}),
            'nomeclinica': forms.TextInput(attrs={'class': 'form-control'}),
            'logotipo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }