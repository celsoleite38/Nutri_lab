import nutribr
from .models import Alimento

taco = Taco()

def buscar_alimento(nome):
    """Busca alimento no nutribr e salva no banco se não existir."""
    resultado = taco.search_food(nome)
    if resultado:
        alimento = Alimento.objects.create(
            nome=resultado["description"],
            energia=resultado.get("energy_kcal"),
            proteina=resultado.get("protein_g"),
            carboidrato=resultado.get("carbohydrate_g"),
            lipidio=resultado.get("lipid_g"),
            fibra=resultado.get("fiber_g"),
        )
        return alimento
    return None
