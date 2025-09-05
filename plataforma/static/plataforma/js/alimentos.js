// static/plataforma/js/alimentos.js
document.addEventListener('DOMContentLoaded', function() {
    // Busca de alimentos
    document.getElementById('btnBuscarAlimento').addEventListener('click', buscarAlimentos);
    document.getElementById('inputBuscarAlimento').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') buscarAlimentos();
    });

    function buscarAlimentos() {
        const termo = document.getElementById('inputBuscarAlimento').value;
        if (termo.length < 2) return;

        fetch(`/alimentos/buscar-ajax/?termo=${encodeURIComponent(termo)}`)
            .then(response => response.json())
            .then(data => mostrarResultados(data));
    }

    function mostrarResultados(alimentos) {
        const container = document.getElementById('resultadosAlimentos');
        container.innerHTML = '';

        alimentos.forEach(alimento => {
            const card = `
                <div class="col-md-6 mb-3">
                    <div class="card alimento-card" data-id="${alimento.id}">
                        <div class="card-body">
                            <h6 class="card-title">${alimento.nome}</h6>
                            <p class="card-text mb-1">
                                <small>${alimento.categoria} • ${alimento.medida_caseira}</small>
                            </p>
                            <p class="card-text mb-1">
                                <small>${alimento.energia_kcal} kcal • ${alimento.proteina_g}g prot • ${alimento.carboidrato_g}g carb</small>
                            </p>
                            <button class="btn btn-sm btn-success btn-adicionar" data-id="${alimento.id}">
                                <i class="fas fa-plus"></i> Adicionar
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += card;
        });

        // Adiciona event listeners aos botões
        document.querySelectorAll('.btn-adicionar').forEach(btn => {
            btn.addEventListener('click', function() {
                const alimentoId = this.getAttribute('data-id');
                adicionarAlimentoPlano(alimentoId);
            });
        });
    }

    function adicionarAlimentoPlano(alimentoId) {
        // Implemente a adição ao plano aqui
        alert(`Alimento ${alimentoId} será adicionado ao plano!`);
    }
});