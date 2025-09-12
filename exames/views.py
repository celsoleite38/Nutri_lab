# exames/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SolicitacaoExame, ResultadoExame, TipoExame
from plataforma.models import Pacientes
from django.utils import timezone
from autenticacao.models import PerfilProfissional


def listar_solicitacoes(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id)
    solicitacoes = SolicitacaoExame.objects.filter(paciente=paciente).order_by('-data_solicitacao')
    
    context = {
        'paciente': paciente,
        'solicitacoes': solicitacoes,
    }
    return render(request, 'exames/listar_solicitacoes.html', context)


def nova_solicitacao(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id)
    
    if request.method == "POST":
        # Cria a solicitação principal
        data_solicitacao = request.POST.get("data_solicitacao")
        if not data_solicitacao:
            messages.error(request, "A data da solicitação é obrigatória.")
            return redirect('exames:nova_solicitacao', paciente_id=paciente.id)

        solicitacao = SolicitacaoExame(
            paciente=paciente,
            data_solicitacao=data_solicitacao,
            status='P' # Pendente
        )
        solicitacao.save()
        messages.success(request, "Solicitação criada com sucesso! Agora adicione os exames.")
        # Redireciona para a página de detalhes para adicionar os itens
        return redirect('exames:detalhe_solicitacao', solicitacao_id=solicitacao.id)

    context = {
        'paciente': paciente,
        'data_hoje': timezone.now().strftime('%Y-%m-%d') # Sugere a data de hoje
    }
    return render(request, 'exames/nova_solicitacao.html', context)


def detalhe_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoExame, id=solicitacao_id)
    paciente = solicitacao.paciente
    
    # Lógica para adicionar um novo EXAME SOLICITADO (sem resultado)
    if 'adicionar_exame' in request.POST:
        tipo_exame_id = request.POST.get("tipo_exame")
        if not tipo_exame_id:
            messages.error(request, "Selecione um exame para adicionar à solicitação.")
        else:
            tipo_exame = get_object_or_404(TipoExame, id=tipo_exame_id)
            if not ResultadoExame.objects.filter(solicitacao=solicitacao, tipo_exame=tipo_exame).exists():
                # Cria o item SEM resultado
                ResultadoExame.objects.create(solicitacao=solicitacao, tipo_exame=tipo_exame)
                messages.success(request, f"Exame '{tipo_exame.nome}' solicitado com sucesso.")
            else:
                messages.warning(request, f"O exame '{tipo_exame.nome}' já está nesta solicitação.")
        return redirect('exames:detalhe_solicitacao', solicitacao_id=solicitacao.id)

    
    if 'atualizar_resultados' in request.POST:
        for key, value in request.POST.items():
            if key.startswith("resultado_"):
                resultado_id = key.split("_")[1]
                try:
                    resultado_exame = ResultadoExame.objects.get(id=resultado_id, solicitacao=solicitacao)
                    if value: # Só atualiza se o campo não estiver vazio
                        resultado_exame.resultado = value.replace(',', '.') 
                        resultado_exame.save()
                except (ResultadoExame.DoesNotExist, ValueError):
                    continue
        solicitacao.atualizar_status()
        messages.success(request, "Resultados atualizados com sucesso!")
        return redirect('exames:detalhe_solicitacao', solicitacao_id=solicitacao.id)

    resultados_existentes = ResultadoExame.objects.filter(solicitacao=solicitacao).order_by('tipo_exame__nome')
    ids_existentes = resultados_existentes.values_list('tipo_exame_id', flat=True)
    tipos_de_exame_disponiveis = TipoExame.objects.exclude(id__in=ids_existentes).order_by('nome')

    context = {
        'solicitacao': solicitacao,
        'paciente': paciente,
        'tipos_de_exame': tipos_de_exame_disponiveis,
        'resultados': resultados_existentes,
    }
    return render(request, 'exames/detalhe_solicitacao.html', context)

def imprimir_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoExame, id=solicitacao_id)
    paciente = solicitacao.paciente

    perfil_profissional = None
    if paciente.nutri:
        try:
            # 2. Buscar usando o modelo CORRETO
            perfil_profissional = PerfilProfissional.objects.get(usuario=paciente.nutri)
        except PerfilProfissional.DoesNotExist:
            perfil_profissional = None

    exames_solicitados = ResultadoExame.objects.filter(solicitacao=solicitacao).order_by('tipo_exame__nome')

    context = {
        'paciente': paciente,
        'solicitacao': solicitacao,
        'exames_solicitados': exames_solicitados,
        'perfil': perfil_profissional,
        'data_atual': timezone.now().date(),
    }
    
    return render(request, 'exames/imprimir_solicitacao.html', context)
