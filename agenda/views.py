from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, TemplateView, UpdateView
from .models import Consulta
from .forms import AgendamentoForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required # Para a função de cancelamento
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_POST # Para garantir que o cancelamento seja POST
from datetime import timedelta

# Função auxiliar unificada para obter a cor do status
def get_cor_status(status):
    cores = {
        "agendado": "#3498db",
        "confirmado": "#2ecc71",
        "cancelado": "#e74c3c",
        "realizado": "#9b59b6"
    }
    return cores.get(status, "#3498db")

class CriarAgendamentoView(LoginRequiredMixin, CreateView):
    model = Consulta
    form_class = AgendamentoForm
    template_name = "agenda/criar_agendamento.html"
    success_url = reverse_lazy("agenda:calendario")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.profissional = self.request.user
        return super().form_valid(form)

class EditarConsultaView(LoginRequiredMixin, UpdateView):
    model = Consulta
    form_class = AgendamentoForm
    template_name = "agenda/editar_consulta.html"

    def get_success_url(self):
        return reverse_lazy("agenda:detalhes_consulta", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return Consulta.objects.filter(profissional=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

@login_required
@require_POST # Garante que esta view só aceite requisições POST
def cancelar_consulta_view(request, pk):
    try:
        consulta = get_object_or_404(Consulta, pk=pk)

        # Verifica se o usuário logado é o profissional da consulta
        if consulta.profissional != request.user:
            return JsonResponse({"success": False, "message": "Você não tem permissão para cancelar esta consulta."}, status=403)
        
        # Verifica se a consulta já está cancelada ou realizada
        if consulta.status == "cancelado":
            return JsonResponse({"success": False, "message": "Esta consulta já está cancelada."}, status=400)
        if consulta.status == "realizado":
            return JsonResponse({"success": False, "message": "Não é possível cancelar uma consulta já realizada."}, status=400)

        consulta.status = "cancelado" # Define o status como cancelado
        consulta.save()
        return JsonResponse({"success": True, "message": "Consulta cancelada com sucesso!"})

    except Consulta.DoesNotExist:
        return JsonResponse({"success": False, "message": "Consulta não encontrada."}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Ocorreu um erro: {str(e)}"}, status=500)
# Fim da função cancelar_consulta_view - Certifique-se de que a próxima função está corretamente desindentada.

def detalhes_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, profissional=request.user)
    return render(request, "agenda/detalhes_consulta.html", {"consulta": consulta})

class CalendarioView(LoginRequiredMixin, TemplateView):
    template_name = "agenda/calendario.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def consultas_json(request):
    consultas = Consulta.objects.filter(profissional=request.user)
    eventos = []
    for consulta in consultas:
        eventos.append({
            "id": consulta.id,
            "title": f"{consulta.paciente.nome} ({consulta.get_status_display()})",
            "start": consulta.data_hora.isoformat(),
            "end": (consulta.data_hora + timedelta(minutes=consulta.duracao)).isoformat(),
            "color": get_cor_status(consulta.status),
            "extendedProps": {
                "paciente_id": consulta.paciente.id,
                "telefone": consulta.paciente.telefone,
                "observacoes": consulta.observacoes,
                "status": consulta.status
            }
        })
    return JsonResponse(eventos, safe=False)

