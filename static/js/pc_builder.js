document.addEventListener("DOMContentLoaded", function() {
    
    // Gestione dei filtri per la ricerca dei componenti del PC
    const searchInput = document.querySelector('[data-js="search-input"]');
    const productCards = document.querySelectorAll('[data-js="product-card"]');
    const productsList = document.querySelector('[data-js="products-list"]');
    
    if (searchInput && productCards.length > 0) {
        // Crea dinamicamente un messaggio da mostrare se la ricerca non produce risultati
        const noResultsMsg = document.createElement("div");
        noResultsMsg.className = "empty-state";
        noResultsMsg.style.display = "none";
        noResultsMsg.textContent = "Nessun prodotto corrisponde alla ricerca.";
        
        if (productsList) {
            productsList.appendChild(noResultsMsg);
        }

        searchInput.addEventListener("input", function(e) {
            const query = e.target.value.toLowerCase().trim();
            let visibleCount = 0;

            // Controlla ogni card di prodotto per vedere se corrisponde al testo cercato
            productCards.forEach(function(card) {
                const title = card.getAttribute("data-name").toLowerCase();
                const desc = card.getAttribute("data-desc").toLowerCase();

                if (title.includes(query) || desc.includes(query)) {
                    card.style.display = "flex"; // Mostra la card
                    visibleCount++;
                } else {
                    card.style.display = "none"; // Nasconde la card
                }
            });

            // Mostra o nasconde il messaggio di "nessun risultato" a seconda dei prodotti trovati
            if (visibleCount === 0) {
                noResultsMsg.style.display = "block";
            } else {
                noResultsMsg.style.display = "none";
            }
        });
    }

    const clearBtn = document.querySelector('[data-js="clear-build"]');
    if (clearBtn) {
        clearBtn.addEventListener("click", function(e) {
            const confirmClear = confirm("Sei sicuro di voler resettare e cancellare tutti i componenti scelti finora?");
            if (!confirmClear) {
                e.preventDefault();
            }
        });
    }
});
