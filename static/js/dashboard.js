// Attende il caricamento completo del DOM
document.addEventListener('DOMContentLoaded', function() {
    
    // Gestione della ricerca e del filtraggio nelle tabelle della dashboard
    const searchInputs = document.querySelectorAll('[data-js="search-table"]');
    
    searchInputs.forEach(function(input) {
        const tableId = input.getAttribute('data-search-table');
        const table = document.getElementById(tableId);
        
        if (!table) return;

        // Filtra le righe della tabella ogni volta che l'utente rilascia un tasto
        input.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                // Mostra la riga se contiene il testo cercato, altrimenti la nasconde
                if (text.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });

    // Impedisce che cliccando su link o input all'interno di un tag <summary>
    // venga attivata/disattivata la visualizzazione dei dettagli del tag <details>
    const summaryInteractives = document.querySelectorAll('summary [data-js="search-table"], summary [data-js="add-button"]');
    summaryInteractives.forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.stopPropagation(); 
        });
    });
});
