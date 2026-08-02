from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from autenticacao.models import PerfilProfissional
from exames.models import ResultadoExame
from .models import Pacientes, DadosPaciente, Refeicao, PlanoAlimentar, ItemRefeicao
from datetime import date, datetime
from django.views.decorators.csrf import csrf_exempt
from alimentos.models import Alimento
from decimal import Decimal, InvalidOperation
import json
from django.urls import reverse
from django.db.models import Q


@login_required(login_url='/auth/logar/')
def pacientes(request):
    if request.method =="GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        query = request.GET.get('q')
        if query:
            pacientes = pacientes.filter(nome__icontains=query)
        return render(request, 'pacientes.html' , {'pacientes' : pacientes})
    elif request.method == "POST":
        nome = request.POST.get('nome', '')
        cpf = request.POST.get('cpf', '')
        sexo = request.POST.get('sexo', '')
        estadocivil = request.POST.get('estadocivil', '')
        datanascimento = request.POST.get('datanascimento', '')
        naturalidade = request.POST.get('naturalidade', '')
        profissao = request.POST.get('profissao', '')
        email = request.POST.get('email', '')
        telefone = request.POST.get('telefone', '')
        endereco = request.POST.get('endereco', '')
        restricao_diabetico = request.POST.get('restricao_diabetico') == 'on'
        restricao_hipertenso = request.POST.get('restricao_hipertenso') == 'on'
        restricao_outros = request.POST.get('restricao_outros', '').strip()
        
        if any(len(campo.strip()) == 0 for campo in [
            nome, sexo, cpf, estadocivil, datanascimento,
            naturalidade, profissao, email, telefone, endereco
        ]):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/plataforma/pacientes/')
            
        
    
            
        paciente = Pacientes.objects.filter(email=email)
        
        if paciente.exists():
                messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse E-mail')
                return redirect('/plataforma/pacientes/')
            
        try:
            p1 = Pacientes(
                nome=nome,
                cpf=cpf,
                sexo=sexo,
                estadocivil=estadocivil,
                datanascimento=datanascimento,
                naturalidade=naturalidade,
                profissao=profissao,
                email=email,
                telefone=telefone,
                endereco=endereco,
                restricao_diabetico=restricao_diabetico,
                restricao_hipertenso=restricao_hipertenso,
                restricao_outros=restricao_outros,
                nutri=request.user
            )
                
            p1.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso')
            return redirect('/plataforma/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro Interno')
            return redirect('/plataforma/pacientes/')

@login_required(login_url='/auth/logar/')
def dados_paciente_listar(request):
    if request.method == "GET":
        query = request.GET.get('q', '')
        pacientes = Pacientes.objects.filter(nutri=request.user)
        if query:
            pacientes = pacientes.filter(nome__icontains=query)
        
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})
        
    


@login_required(login_url='/auth/logar/')
def dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect(reverse('plataforma:pacientes'))
   
    if request.method == "GET":
        dados_paciente = DadosPaciente.objects.filter(paciente=paciente).order_by('-data')
        
        return render(request, 'dados_paciente.html', {
            'paciente': paciente, 
            'dados_paciente': dados_paciente
        })
    
    elif request.method == "POST":
        try:
            # Função para converter e validar valores decimais
            def parse_decimal(value, default='0'):
                if not value or value.strip() == '':
                    return Decimal(default)
                # Substituir vírgula por ponto para formato decimal
                value = value.replace(',', '.')
                try:
                    return Decimal(value)
                except InvalidOperation:
                    return Decimal(default)
            
            # Converter todos os valores decimais
            peso = parse_decimal(request.POST.get('peso'))
            altura = parse_decimal(request.POST.get('altura'))
            gordura = parse_decimal(request.POST.get('gordura'))
            musculo = parse_decimal(request.POST.get('musculo'))
            
            
            # Criar instância de DadosPaciente (não sobrescrever a variável paciente)
            dados_paciente = DadosPaciente(
                paciente=paciente,
                data=datetime.now(),
                peso=peso,
                altura=altura,
                percentual_gordura=gordura,
                percentual_musculo=musculo,
                
            )
            
            dados_paciente.save()
            
            messages.add_message(request, constants.SUCCESS, 'Dados cadastrados com sucesso')
            return redirect(reverse('plataforma:dados_paciente', kwargs={'id': id}))
            
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Erro ao salvar dados: {str(e)}')
            return redirect(reverse('plataforma:dados_paciente', kwargs={'id': id}))



@login_required(login_url='/auth/logar/')
@csrf_exempt
def grafico_peso(request, id):
    paciente = get_object_or_404(Pacientes, id=id, nutri=request.user)
    dados = DadosPaciente.objects.filter(paciente=paciente).order_by("data")
    pesos = []
    gorduras = []
    musculos = []
    labels = []
    
    for dado in dados:
        if dado.peso is not None:
            pesos.append(float(dado.peso))
        else:
            pesos.append(None)
            
        if dado.percentual_gordura is not None:
            gorduras.append(float(dado.percentual_gordura))
        else:
            gorduras.append(None)
            
        if dado.percentual_musculo is not None:
            musculos.append(float(dado.percentual_musculo))
        else:
            musculos.append(None)
            
        labels.append(dado.data.strftime("%d/%m/%Y") if dado.data else "")
    
    data = {
        'peso': pesos,
        'percentual_gordura': gorduras,
        'percentual_musculo': musculos,
        'labels': labels
    }
    return JsonResponse(data)

@login_required(login_url='/auth/logar/')
def plano_alimentar_listar(request):
    if request.method == "GET":
        query = request.GET.get('q', '').strip()
        aba_ativa = request.GET.get('tab', 'pacientes')

        # Buscar pacientes do nutricionista logado
        pacientes = Pacientes.objects.filter(nutri=request.user)

        # Buscar planos do nutricionista logado
        planos = PlanoAlimentar.objects.filter(
            paciente__nutri=request.user
        ).select_related('paciente').prefetch_related('refeicoes').order_by('-data_criacao')

        # Se o usuário digitou algo na busca:
        if query:
            # Filtra pacientes por NOME ou CPF
            pacientes = pacientes.filter(
                Q(nome__icontains=query) | Q(cpf__icontains=query)
            )

            # Filtra planos por NOME DO PLANO ou NOME DO PACIENTE
            planos = planos.filter(
                Q(nome__icontains=query) | Q(paciente__nome__icontains=query)
            )

        return render(
            request,
            'plano_alimentar_listar.html',
            {
                'pacientes': pacientes,
                'planos': planos,
                'query': query,
                'aba_ativa': aba_ativa,
            },
        )
    
@login_required(login_url='/auth/logar/')
def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect(reverse('plataforma:plano_alimentar_listar'))
    
    if request.method == "GET":
        # Use o novo sistema de refeições
        plano = PlanoAlimentar.objects.filter(paciente=paciente).first()
        refeicoes = Refeicao.objects.filter(paciente=paciente).order_by("horario")
        
        return render(request, 'plano_alimentar.html', {
            'paciente': paciente, 
            'refeicoes': refeicoes,
            'plano': plano
        })
    
    
@login_required(login_url='/auth/logar/')    
def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect(reverse('plataforma:dados_paciente_listar'))
    
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        
        r1 = Refeicao(paciente=paciente,
                        titulo=titulo,
                        horario=horario)
        
        r1.save()
        
        messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
        return redirect(reverse('plataforma:plano_alimentar', args=[id_paciente]))

@login_required(login_url='/auth/logar/')
def imprimir_dados_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)

    if paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plataforma:pacientes')

    from exames.models import SolicitacaoExame, ResultadoExame

    dados_paciente = DadosPaciente.objects.filter(paciente=paciente).order_by('-data')
    perfil = PerfilProfissional.objects.filter(usuario=request.user).first()

    # Buscar todos os resultados de exames do paciente com resultado preenchido
    resultados_exames = ResultadoExame.objects.filter(
        solicitacao__paciente=paciente,
        resultado__isnull=False
    ).select_related('tipo_exame', 'solicitacao').order_by('solicitacao__data_solicitacao', 'tipo_exame__nome')

    return render(request, 'imprimir_dados_paciente.html', {
        'paciente': paciente,
        'dados_paciente': dados_paciente,
        'resultados_exames': resultados_exames,
        'perfil': perfil,
        'today': date.today(),
    })
    
@login_required(login_url='/auth/logar/')
def editar_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('/plataforma/pacientes/')
    if request.method == "POST":
        paciente.nome = request.POST.get('nome', '')
        paciente.cpf = request.POST.get('cpf', '')
        paciente.sexo = request.POST.get('sexo', '')
        paciente.estadocivil = request.POST.get('estadocivil', '')
        paciente.datanascimento = request.POST.get('datanascimento', '')
        paciente.naturalidade = request.POST.get('naturalidade', '')
        paciente.profissao = request.POST.get('profissao', '')
        paciente.email = request.POST.get('email', '')
        paciente.telefone = request.POST.get('telefone', '')
        paciente.endereco = request.POST.get('endereco', '')
        paciente.restricao_diabetico = request.POST.get('restricao_diabetico') == 'on'
        paciente.restricao_hipertenso = request.POST.get('restricao_hipertenso') == 'on'
        paciente.restricao_outros = request.POST.get('restricao_outros', '').strip()
        
        if any(len(campo.strip()) == 0 for campo in [
            paciente.nome, paciente.sexo, paciente.estadocivil, paciente.datanascimento,
            paciente.naturalidade, paciente.profissao, paciente.email, paciente.telefone,
            paciente.endereco
        ]):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect(f'/plataforma/editar_paciente/{id}/')

        try:
            paciente.datanascimento = datetime.strptime(paciente.datanascimento, '%Y-%m-%d').date()
            paciente.save()
            messages.add_message(request, constants.SUCCESS, 'Paciente atualizado com sucesso!')
            return redirect('/plataforma/pacientes/')
        except:
            messages.add_message(request, constants.ERROR, 'Erro ao atualizar paciente')
            messages.add_message(request, constants.ERROR, 'Data de nascimento inválida')
            return redirect(f'/plataforma/editar_paciente/{id}/')

    return render(request, 'editar_paciente.html', {'paciente': paciente})


@login_required(login_url='/auth/logar/')
def imprimir_paciente(request, id):
    paciente = get_object_or_404(Pacientes, id=id)

    if paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect(reverse('plataforma:pacientes'))

    from exames.models import ResultadoExame

    dados_paciente = DadosPaciente.objects.filter(paciente=paciente).order_by('-data')
    perfil = PerfilProfissional.objects.filter(usuario=request.user).first()

    resultados_exames = ResultadoExame.objects.filter(
        solicitacao__paciente=paciente,
        resultado__isnull=False
    ).select_related('tipo_exame', 'solicitacao').order_by('solicitacao__data_solicitacao', 'tipo_exame__nome')

    return render(request, 'imprimir_dados_paciente.html', {
        'paciente': paciente,
        'dados_paciente': dados_paciente,
        'resultados_exames': resultados_exames,
        'perfil': perfil,
        'today': date.today(),
    })


@login_required(login_url='/auth/logar/')
def calcular_nutrientes_plano(request, plano_id):
    plano = get_object_or_404(
        PlanoAlimentar.objects.prefetch_related('refeicoes__itens__alimento'),
        id=plano_id
    )
    total_nutrientes = {
        'energia': 0, 'proteinas': 0, 'carboidratos': 0, 
        'lipidios': 0, 'fibras': 0
    }
    
    for refeicao in plano.refeicoes.all():
        for item in refeicao.itens.all():
            nutrientes = item.nutrientes_totais()
            for key in total_nutrientes:
                total_nutrientes[key] += nutrientes.get(key, 0)
    
    return JsonResponse(total_nutrientes)

@login_required(login_url='/auth/logar/')
def criar_plano_alimentar(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        objetivo = request.POST.get('objetivo')
        
        plano = PlanoAlimentar(
            paciente=paciente,
            nome=nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            objetivo=objetivo
        )
        plano.save()
        
        messages.success(request, 'Plano alimentar criado com sucesso!')
        return redirect('plataforma:detalhes_plano_alimentar', plano_id=plano.id)
    
    return render(request, 'criar_plano_alimentar.html', {'paciente': paciente})


# Substitua a função detalhes_plano_alimentar em plataforma/views.py

@login_required(login_url='/auth/logar/')
def detalhes_plano_alimentar(request, plano_id):
    plano = get_object_or_404(
        PlanoAlimentar.objects.prefetch_related('refeicoes__itens__alimento'),
        id=plano_id
    )

    if plano.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plataforma:plano_alimentar_listar')

    if request.method == 'POST':
        refeicao_id = request.POST.get('refeicao_id')
        if refeicao_id:
            refeicao = get_object_or_404(Refeicao, id=refeicao_id)
            if refeicao.paciente != plano.paciente:
                messages.error(request, 'Essa refeição não pertence a este paciente.')
            else:
                plano.refeicoes.add(refeicao)
                messages.success(request, f'Refeição "{refeicao.titulo}" adicionada ao plano.')
        return redirect(reverse('plataforma:detalhes_plano_alimentar', args=[plano.id]))

    # Pré-calcular nutrientes por refeição (evita chamar métodos no template)
    refeicoes_com_nutrientes = []
    for refeicao in plano.refeicoes.all().order_by('horario'):
        nutrientes = refeicao.total_nutrientes()
        refeicoes_com_nutrientes.append({
            'refeicao': refeicao,
            'itens': refeicao.itens.select_related('alimento').all(),
            'nutrientes': nutrientes,
        })

    # Refeições disponíveis para adicionar ao plano
    refeicoes_disponiveis = Refeicao.objects.filter(
        paciente=plano.paciente
    ).exclude(id__in=plano.refeicoes.values_list('id', flat=True))

    # Totais diários
    duracao_dias = plano.duracao_dias()
    total_nutrientes = plano.total_nutrientes()
    nutrientes_diarios = total_nutrientes

    return render(request, 'detalhes_plano_alimentar.html', {
        'plano': plano,
        'refeicoes_com_nutrientes': refeicoes_com_nutrientes,
        'refeicoes_disponiveis': refeicoes_disponiveis,
        'nutrientes_diarios': nutrientes_diarios,
        'duracao_dias': duracao_dias,
    })


@login_required(login_url='/auth/logar/')
def adicionar_refeicao(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        observacoes = request.POST.get('observacoes', '')
        
        refeicao = Refeicao(
            paciente=paciente,
            tipo=tipo,
            titulo=titulo,
            horario=horario,
            observacoes=observacoes
        )
        refeicao.save()
        
        messages.success(request, 'Refeição criada com sucesso!')
        return redirect('plataforma:editar_refeicao', refeicao_id=refeicao.id)
    
    return render(request, 'adicionar_refeicao.html', {
        'paciente': paciente,
        'tipos_refeicao': Refeicao.TIPO_CHOICES
    })

@login_required(login_url='/auth/logar/')
def editar_refeicao(request, refeicao_id):
    refeicao = get_object_or_404(Refeicao.objects.select_related('paciente'), id=refeicao_id)
    if refeicao.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect(reverse('plataforma:plano_alimentar_listar'))
    
    alimentos = Alimento.objects.filter(ativo=True)
    
    if request.method == 'POST':
        # Adicionar alimento à refeição
        alimento_id = request.POST.get('alimento_id')
        quantidade = request.POST.get('quantidade', 100)
        observacoes = request.POST.get('observacoes', '')
        
        if alimento_id:
            alimento = get_object_or_404(Alimento, id=alimento_id)
            item = ItemRefeicao(
                refeicao=refeicao,
                alimento=alimento,
                quantidade_g=quantidade,
                observacoes=observacoes
            )
            item.save()
            messages.success(request, f'{alimento.nome} adicionado à refeição.')
    
    itens = refeicao.itens.select_related('alimento').prefetch_related('substituicoes__alimento_substituto')
    itens_info = []
    for item in itens:
        permitido, motivo = refeicao.paciente.alimento_permitido(item.alimento)
        itens_info.append({
            'item': item,
            'permitido': permitido,
            'motivo': motivo,
            'substituicoes': item.substituicoes.all(),
        })

    return render(request, 'editar_refeicao.html', {
        'refeicao': refeicao,
        'paciente': refeicao.paciente,
        'restricoes_paciente': refeicao.paciente.restricoes_lista(),
        'alimentos': alimentos,
        'itens': itens,
        'itens_info': itens_info,
        'total_nutrientes': refeicao.total_nutrientes()
    })


    
@login_required(login_url='/auth/logar/')
def remover_refeicao(request, refeicao_id):
    # Encontre a refeição e verifique permissões
    refeicao = get_object_or_404(Refeicao, id=refeicao_id)
    
    # Verifique se o usuário tem permissão para esta refeição
    if refeicao.paciente.nutri != request.user:
        messages.error(request, 'Você não tem permissão para remover esta refeição.')
        return redirect(reverse('plataforma:plano_alimentar', args=[refeicao.paciente.id]))
    
    if request.method == 'POST':
        # Salve o ID do paciente antes de deletar
        paciente_id = refeicao.paciente.id
        
        # DELETA COMPLETAMENTE A REFEIÇÃO
        refeicao.delete()
        
        messages.success(request, 'Refeição removida com sucesso!')
        return redirect('plataforma:plano_alimentar', id=paciente_id)
    
    return redirect('plataforma:plano_alimentar', id=refeicao.paciente.id)


@login_required(login_url='/auth/logar/')
def remover_item_refeicao(request, item_id):
    item = get_object_or_404(ItemRefeicao, id=item_id)
    if item.refeicao.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plataforma:plano_alimentar_listar')
    
    refeicao_id = item.refeicao.id
    item.delete()
    messages.success(request, 'Item removido da refeição.')
    return redirect('plataforma:editar_refeicao', refeicao_id=refeicao_id)

@login_required(login_url='/auth/logar/')
def buscar_alimentos_refeicao(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        termo = request.GET.get('q', '')
        alimentos = Alimento.objects.filter(
            nome__icontains=termo, 
            ativo=True
        ).select_related('categoria')[:10]
        
        resultados = [{
            'id': a.id,
            'nome': a.nome,
            'categoria': a.categoria.nome if a.categoria else '',
            'medida': a.medida_caseira,
            'energia': float(a.energia_kcal),
            'proteinas': float(a.proteina_g),
            'carboidratos': float(a.carboidrato_g),
            'lipidios': float(a.lipidios_g)
        } for a in alimentos]
        
        return JsonResponse(resultados, safe=False)

@login_required(login_url='/auth/logar/')
def calcular_nutrientes_item(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            alimento_id = request.POST.get('alimento_id')
            quantidade = float(request.POST.get('quantidade', 100))
            
            alimento = get_object_or_404(Alimento, id=alimento_id)
            nutrientes = alimento.calcular_nutrientes_por_porcao(quantidade)
            
            return JsonResponse({
                'success': True,
                'nutrientes': nutrientes
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})


@login_required(login_url='/auth/logar/')
def sugerir_substituicoes(request, item_id):
    item = get_object_or_404(ItemRefeicao, id=item_id)
    if item.refeicao.paciente.nutri != request.user:
        return JsonResponse({'success': False, 'error': 'Acesso negado'})

    paciente = item.refeicao.paciente
    alimento_original = item.alimento
    qtd_original = float(item.quantidade_g)

    # Candidatos: mesma categoria, ativos, diferentes do atual
    candidatos = Alimento.objects.filter(
        categoria=alimento_original.categoria,
        ativo=True
    ).exclude(id=alimento_original.id)

    # Remove alimentos já presentes na refeição
    ids_na_refeicao = item.refeicao.itens.values_list('alimento_id', flat=True)
    candidatos = candidatos.exclude(id__in=ids_na_refeicao)

    # Filtra incompatíveis com as restrições do paciente
    permitidos = []
    for candidato in candidatos:
        permitido, _ = paciente.alimento_permitido(candidato)
        if permitido:
            permitidos.append(candidato)

    def proximidade(c):
        """Menor desvio = mais próximo nutricionalmente"""
        campos = ['energia_kcal', 'proteina_g', 'carboidrato_g', 'lipidios_g', 'fibra_alimentar_g']
        total = 0.0
        for campo in campos:
            a = float(getattr(alimento_original, campo)) + 0.001
            b = float(getattr(c, campo)) + 0.001
            total += abs(a - b) / max(a, b)
        return total

    permitidos.sort(key=proximidade)
    sugestoes = permitidos[:5]

    resultados = []
    for cand in sugestoes:
        energia_orig = float(alimento_original.energia_kcal)
        energia_cand = float(cand.energia_kcal)
        if energia_cand > 0:
            qtd_ajustada = qtd_original * energia_orig / energia_cand
        else:
            qtd_ajustada = qtd_original
        qtd_ajustada = round(qtd_ajustada / 5) * 5
        if qtd_ajustada < 5:
            qtd_ajustada = 5

        nutrientes = cand.calcular_nutrientes_por_porcao(qtd_ajustada)
        resultados.append({
            'id': cand.id,
            'nome': cand.nome,
            'medida_caseira': cand.medida_caseira,
            'quantidade_g': qtd_ajustada,
            'energia': nutrientes['energia'],
            'proteina': nutrientes['proteina'],
            'carboidrato': nutrientes['carboidrato'],
            'lipidios': nutrientes['lipidios'],
            'fibra': nutrientes['fibra'],
        })

    return JsonResponse({
        'success': True,
        'alimento_original': alimento_original.nome,
        'sugestoes': resultados
    })


@login_required(login_url='/auth/logar/')
def salvar_substituicoes(request, item_id):
    item = get_object_or_404(ItemRefeicao, id=item_id)
    if item.refeicao.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plataforma:editar_refeicao', refeicao_id=item.refeicao.id)

    if request.method == 'POST':
        selecionados = request.POST.getlist('substituto_id')

        # Remove as substituições anteriores (o nutricionista redefine o que oferecer)
        item.substituicoes.all().delete()

        for alimento_id in selecionados:
            try:
                alimento = Alimento.objects.get(id=alimento_id)
            except Alimento.DoesNotExist:
                continue
            try:
                quantidade = Decimal(request.POST.get(f'quantidade_{alimento_id}', ''))
            except (InvalidOperation, TypeError):
                quantidade = item.quantidade_g

            item.substituicoes.create(
                alimento_substituto=alimento,
                quantidade_g=quantidade,
            )

        if selecionados:
            messages.success(request, f'{len(selecionados)} substituição(ões) salva(s).')
        else:
            messages.info(request, 'Nenhuma substituição selecionada.')

    return redirect('plataforma:editar_refeicao', refeicao_id=item.refeicao.id)


@login_required(login_url='/auth/logar/')
def desativar_plano(request, plano_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    
    # Verifica se o usuário tem permissão (nutricionista do paciente)
    if plano.paciente.nutri != request.user:
        messages.error(request, "Você não tem permissão para desativar este plano.")
        return redirect(reverse('plataforma:plano_alimentar_listar'))
    
    # Desativa o plano
    plano.ativo = False
    plano.save()
    
    messages.success(request, f"Plano '{plano.nome}' desativado com sucesso!")
    return redirect(reverse('plataforma:detalhes_plano_alimentar', args=[plano.id]))

@login_required(login_url='/auth/logar/')
def reativar_plano(request, plano_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    
    if plano.paciente.nutri != request.user:
        messages.error(request, "Você não tem permissão para reativar este plano.")
        return redirect(reverse('plataforma:plano_alimentar_listar'))
    
    # Reativa o plano
    plano.ativo = True
    plano.save()
    
    messages.success(request, f"Plano '{plano.nome}' reativado com sucesso!")
    return redirect(reverse('plataforma:detalhes_plano_alimentar', args=[plano.id]))


@login_required(login_url='/auth/logar/')
def remover_refeicao_plano(request, plano_id, refeicao_id):
    plano = get_object_or_404(PlanoAlimentar, id=plano_id)
    refeicao = get_object_or_404(Refeicao, id=refeicao_id)
    
    # Verifica permissões
    if plano.paciente.nutri != request.user or refeicao.paciente.nutri != request.user:
        messages.error(request, "Você não tem permissão para realizar esta ação.")
        return redirect(reverse('plataforma:plano_alimentar_listar'))
    
    # Remove a refeição do plano
    plano.refeicoes.remove(refeicao)
    
    messages.success(request, f"Refeição '{refeicao.titulo}' removida do plano.")
    return redirect(reverse('plataforma:detalhes_plano_alimentar', args=[plano.id]))

@login_required(login_url='/auth/logar/')
def adicionar_refeicao_existente(request, plano_id):
    if request.method == 'POST':
        plano = get_object_or_404(PlanoAlimentar, id=plano_id)
        refeicao_id = request.POST.get('refeicao_id')
        
        if refeicao_id:
            refeicao = get_object_or_404(Refeicao, id=refeicao_id)
            
            # Verifica permissões
            if plano.paciente.nutri != request.user or refeicao.paciente != plano.paciente:
                messages.error(request, "Você não tem permissão para realizar esta ação.")
                return redirect(reverse('plataforma:detalhes_plano_alimentar', args=[plano.id]))
            
            # Adiciona a refeição ao plano
            plano.refeicoes.add(refeicao)
            messages.success(request, f"Refeição '{refeicao.titulo}' adicionada ao plano.")
        
        return redirect(reverse('plataforma:detalhes_plano_alimentar', args=[plano.id]))
    
@login_required(login_url='/auth/logar/')
def detalhes_paciente_planos(request, paciente_id):
    paciente = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
    planos = PlanoAlimentar.objects.filter(paciente=paciente).select_related('paciente').prefetch_related('refeicoes').order_by('-data_criacao')
    outros_pacientes = Pacientes.objects.filter(nutri=request.user).exclude(id=paciente_id).prefetch_related('planoalimentar_set')
    
    return render(request, 'detalhes_paciente_planos.html', {
        'paciente': paciente,
        'planos': planos,
        'outros_pacientes': outros_pacientes,
    })



@login_required(login_url='/auth/logar/')
def copiar_plano_alimentar(request, paciente_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plano_origem_id = data.get('plano_origem_id')
            
            paciente_destino = get_object_or_404(Pacientes, id=paciente_id, nutri=request.user)
            plano_origem = get_object_or_404(
                PlanoAlimentar.objects.prefetch_related('refeicoes__itens__alimento'),
                id=plano_origem_id
            )
            
            # Verifica se o usuário tem acesso ao plano de origem
            if plano_origem.paciente.nutri != request.user:
                return JsonResponse({'success': False, 'error': 'Acesso negado ao plano de origem'})
            
            nome_novo_plano = f"Plano Alimentar {paciente_destino.nome}"
            
            novo_plano = PlanoAlimentar.objects.create(
                paciente=paciente_destino,
                nome=f"{nome_novo_plano} (Padrão)",
                objetivo=plano_origem.objetivo,
                data_inicio=plano_origem.data_inicio,
                data_fim=plano_origem.data_fim,
                #observacoes=f"Cópia do plano de {plano_origem.paciente.nome}\n{plano_origem.observacoes}",
                ativo=True
            )
            
            # Copia as refeições
            for refeicao in plano_origem.refeicoes.all():
                nova_refeicao = Refeicao.objects.create(
                    paciente=paciente_destino,
                    titulo=refeicao.titulo,
                    tipo=refeicao.tipo,
                    horario=refeicao.horario,
                    observacoes=refeicao.observacoes
                )
                
                # Copia os itens da refeição
                for item in refeicao.itens.all():
                    ItemRefeicao.objects.create(
                        refeicao=nova_refeicao,
                        alimento=item.alimento,
                        quantidade_g=item.quantidade_g,
                        observacoes=item.observacoes
                    )
                
                # Adiciona a refeição ao novo plano
                novo_plano.refeicoes.add(nova_refeicao)
            
            return JsonResponse({'success': True, 'novo_plano_id': novo_plano.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})

@login_required(login_url='/auth/logar/')
def imprimir_plano_alimentar(request, plano_id):
    plano = get_object_or_404(
        PlanoAlimentar.objects.select_related('paciente').prefetch_related(
            'refeicoes__itens__alimento',
            'refeicoes__itens__substituicoes__alimento_substituto'
        ),
        id=plano_id
    )
    if plano.paciente.nutri != request.user:
        messages.error(request, 'Acesso não autorizado.')
        return redirect('plataforma:pacientes')
    perfil = PerfilProfissional.objects.filter(usuario=request.user).first()
    duracao_dias = plano.duracao_dias()
    total_nutrientes = plano.total_nutrientes()
    nutrientes_diarios = total_nutrientes
    
    return render(request, 'imprimir_plano_alimentar.html', {
        'plano': plano,
        'paciente': plano.paciente,
        'perfil': perfil,
        'nutrientes_diarios': nutrientes_diarios,
        'duracao_dias': duracao_dias,
        'today': date.today(),
    })


