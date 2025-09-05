# alimentos/views.py
from django.db.models.aggregates import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Alimento, CategoriaAlimento
from .forms import AlimentoForm, CategoriaAlimentoForm, BuscaAlimentoForm

def lista_alimentos(request):
    form = BuscaAlimentoForm(request.GET or None)
    alimentos = Alimento.objects.filter(ativo=True)
    
    if form.is_valid():
        nome = form.cleaned_data.get('nome')
        categoria = form.cleaned_data.get('categoria')
        
        if nome:
            alimentos = alimentos.filter(Q(nome__icontains=nome) | Q(nome_cientifico__icontains=nome))
        if categoria:
            alimentos = alimentos.filter(categoria=categoria)
    
    # Paginação
    paginator = Paginator(alimentos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_alimentos': alimentos.count()
    }
    return render(request, 'alimentos/lista_alimentos.html', context)

def detalhe_alimento(request, alimento_id):
    alimento = get_object_or_404(Alimento, id=alimento_id)
    return render(request, 'alimentos/detalhe_alimento.html', {'alimento': alimento})

def adicionar_alimento(request):
    if request.method == 'POST':
        form = AlimentoForm(request.POST)
        if form.is_valid():
            alimento = form.save()
            messages.success(request, f'Alimento "{alimento.nome}" adicionado com sucesso!')
            return redirect('alimentos:lista_alimentos')
    else:
        form = AlimentoForm()
    
    return render(request, 'alimentos/form_alimento.html', {'form': form, 'titulo': 'Adicionar Alimento'})

def editar_alimento(request, alimento_id):
    alimento = get_object_or_404(Alimento, id=alimento_id)
    
    if request.method == 'POST':
        form = AlimentoForm(request.POST, instance=alimento)
        if form.is_valid():
            alimento = form.save()
            messages.success(request, f'Alimento "{alimento.nome}" atualizado com sucesso!')
            return redirect('alimentos:detalhe_alimento', alimento_id=alimento.id)
    else:
        form = AlimentoForm(instance=alimento)
    
    return render(request, 'alimentos/form_alimento.html', {'form': form, 'titulo': 'Editar Alimento'})

def buscar_alimentos_ajax(request):
    """View para busca AJAX de alimentos"""
    termo = request.GET.get('termo', '')
    
    if termo:
        alimentos = Alimento.objects.filter(
            Q(nome__icontains=termo) | Q(nome_cientifico__icontains=termo),
            ativo=True
        )[:10]
        
        resultados = []
        for alimento in alimentos:
            resultados.append({
                'id': alimento.id,
                'nome': alimento.nome,
                'categoria': alimento.categoria.nome if alimento.categoria else '',
                'medida_caseira': alimento.medida_caseira,
                'quantidade_medida_caseira': float(alimento.quantidade_medida_caseira),
                'energia_kcal': float(alimento.energia_kcal),
                'proteina_g': float(alimento.proteina_g),
                'carboidrato_g': float(alimento.carboidrato_g),
                'lipidios_g': float(alimento.lipidios_g),
            })
        
        return JsonResponse(resultados, safe=False)
    
    return JsonResponse([], safe=False)

def calcular_nutrientes(request):
    """View para cálculo de nutrientes baseado na quantidade"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        alimento_id = request.POST.get('alimento_id')
        quantidade_g = request.POST.get('quantidade_g')
        
        try:
            alimento = Alimento.objects.get(id=alimento_id)
            quantidade_g = float(quantidade_g)
            nutrientes = alimento.calcular_nutrientes_por_porcao(quantidade_g)
            return JsonResponse({'success': True, 'nutrientes': nutrientes})
        except (Alimento.DoesNotExist, ValueError):
            return JsonResponse({'success': False, 'error': 'Dados inválidos'})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})

# Views para Categorias
def lista_categorias(request):
    categorias = CategoriaAlimento.objects.all()
    return render(request, 'alimentos/lista_categorias.html', {'categorias': categorias})

def adicionar_categoria(request):
    if request.method == 'POST':
        form = CategoriaAlimentoForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" adicionada com sucesso!')
            return redirect('alimentos:lista_categorias')
    else:
        form = CategoriaAlimentoForm()
    
    return render(request, 'alimentos/form_categoria.html', {'form': form, 'titulo': 'Adicionar Categoria'})

# alimentos/views.py
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q  # Adicione Q aqui
from django.db import models  # Adicione esta importação
from .models import Alimento, CategoriaAlimento

def dashboard_nutricional(request):
    # Dados simples para teste
    context = {
        'total_alimentos': Alimento.objects.filter(ativo=True).count(),
        'total_categorias': CategoriaAlimento.objects.count(),
        'alimentos_recentes': Alimento.objects.filter(ativo=True).order_by('-id')[:5],
        'categorias_stats': [],
        'media_nutrientes': {'calorias': 0, 'proteinas': 0, 'carboidratos': 0}
    }
    return render(request, 'alimentos/dashboard.html', context)