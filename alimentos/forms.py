# alimentos/forms.py
from django import forms
from .models import Alimento, CategoriaAlimento

class CategoriaAlimentoForm(forms.ModelForm):
    class Meta:
        model = CategoriaAlimento  # Isso referencia o modelo, não define um novo
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_cientifico': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'energia_kcal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proteina_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'lipidios_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carboidrato_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fibra_alimentar_g': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'calcio_mg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ferro_mg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sodio_mg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vitamina_c_mg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'medida_caseira': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade_medida_caseira': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fonte': forms.TextInput(attrs={'class': 'form-control'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BuscaAlimentoForm(forms.Form):
    nome = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar alimento...',
            'id': 'busca-alimento'
        })
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaAlimento.objects.all(),
        required=False,
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={'class': 'form-control'})
    )