import os
import sys
import django

# CONFIGURAR DJANGO
project_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nutri_lab.settings')
django.setup()

from alimentos.models import Alimento

def verificar_dados_atuais():
    """Verificar como estão os dados atualmente"""
    print("🔍 VERIFICANDO DADOS ATUAIS...")
    
    # Pegar alguns alimentos para verificar
    alimentos = Alimento.objects.all()[:10]
    
    print("📋 PRIMEIROS 10 ALIMENTOS NO BANCO:")
    print("-" * 60)
    
    for alimento in alimentos:
        print(f"ID: {alimento.id}")
        print(f"  Nome: {alimento.nome}")
        print(f"  Categoria: {alimento.categoria.id if alimento.categoria else 'None'} - {alimento.categoria.nome if alimento.categoria else 'None'}")
        print(f"  Energia: {alimento.energia_kcal} kcal")
        print(f"  Proteína: {alimento.proteina_g} g")
        print(f"  Lipídios: {alimento.lipidios_g} g")
        print(f"  Carboidrato: {alimento.carboidrato_g} g")
        print("-" * 40)

if __name__ == "__main__":
    verificar_dados_atuais()