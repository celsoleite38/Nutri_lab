# alimentos/management/commands/marcar_restricoes.py
"""Marca automaticamente a restrição de saúde de cada alimento.

Regras usadas (dados já existentes no banco):
  - DIABETES   -> categoria 'Produtos açucarados' + bebidas com carboidrato > 5g/100g
  - HIPERTENSAO -> sódio >= 400mg/100g (referência OMS para alimento rico em sódio)
  - AMBOS      -> alimentos que atendem as duas condições

Uso:
  python manage.py marcar_restricoes
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from alimentos.models import Alimento


class Command(BaseCommand):
    help = "Marca a restrição de saúde (Diabético/Hipertenso) dos alimentos automaticamente."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Primeiro limpa todas as restrições antes de reaplicar.',
        )

    def handle(self, *args, **options):
        if options['limpar']:
            limpos = Alimento.objects.exclude(restricao='').update(restricao='')
            self.stdout.write(self.style.WARNING(f'Restrições limpas: {limpos}'))

        q_diabetes = Q(categoria__nome='Produtos açucarados') | (
            Q(categoria__nome='Bebidas') & Q(carboidrato_g__gt=5)
        )
        q_hipertenso = Q(sodio_mg__gte=400)

        diabete_id = set(Alimento.objects.filter(q_diabetes).values_list('id', flat=True))
        hipertenso_id = set(Alimento.objects.filter(q_hipertenso).values_list('id', flat=True))

        ambos = diabete_id & hipertenso_id
        so_diabete = diabete_id - hipertenso_id
        so_hipertenso = hipertenso_id - diabete_id

        Alimento.objects.filter(id__in=so_diabete).update(restricao='DIABETES')
        Alimento.objects.filter(id__in=so_hipertenso).update(restricao='HIPERTENSAO')
        Alimento.objects.filter(id__in=ambos).update(restricao='AMBOS')

        self.stdout.write(self.style.SUCCESS(
            f'DIABETES: {len(so_diabete)} | HIPERTENSAO: {len(so_hipertenso)} | AMBOS: {len(ambos)}'
        ))
