
document.addEventListener('DOMContentLoaded', function() {
    const buscaInput = document.getElementById('buscaAlimento');
    const resultadosDiv = document.getElementById('resultadosAlimentos');
    
    buscaInput.addEventListener('input', function(e) {
        const termo = e.target.value;
        if (termo.length > 2) {
            fetch(`/alimentos/buscar-ajax/?termo=${encodeURIComponent(termo)}`)
                .then(response => response.json())
                .then(data => {
                    resultadosDiv.innerHTML = '';
                    data.forEach(alimento => {
                        resultadosDiv.innerHTML += `
                            <div class="col-md-6 mb-2">
                                <div class="card alimento-card" 
                                     data-id="${alimento.id}"
                                     data-nome="${alimento.nome}">
                                    <div class="card-body">
                                        <h6>${alimento.nome}</h6>
                                        <small>${alimento.categoria}</small>
                                        <p class="mb-0">${alimento.medida_caseira}</p>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                });
        }
    });
});