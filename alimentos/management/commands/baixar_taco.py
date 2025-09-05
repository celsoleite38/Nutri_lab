# alimentos/management/commands/baixar_taco.py
import requests
import csv
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Baixa dados da TACO/UNICAMP'
    
    def handle(self, *args, **options):
        # Exemplo de como baixar dados (precisa adaptar para o site real)
        try:
            # URL exemplo - precisa verificar a URL real da TACO
            url = "https://www.nepa.unicamp.br/taco/dados/tabela_completa.csv"
            
            response = requests.get(url)
            if response.status_code == 200:
                # Processar o CSV
                lines = response.text.splitlines()
                reader = csv.DictReader(lines)
                
                # Salvar no arquivo local
                with open('alimentos/data/taco_completo.csv', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                self.stdout.write(self.style.SUCCESS('Dados da TACO baixados com sucesso!'))
            else:
                self.stdout.write(self.style.WARNING('Não foi possível baixar os dados automaticamente'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao baixar dados: {e}'))