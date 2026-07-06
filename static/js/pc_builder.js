document.addEventListener("DOMContentLoaded", () => {
    // Filtri
    const searchInput = document.querySelector(".js-search-input");
    const productCards = document.querySelectorAll(".js-product-card");
    const productsList = document.querySelector(".js-products-list");
    
    if (searchInput && productCards.length > 0) {
        // Messaggio per non risultati
        const noResultsMsg = document.createElement("div");
        noResultsMsg.className = "empty-state";
        noResultsMsg.style.display = "none";
        noResultsMsg.textContent = "Nessun prodotto corrisponde alla ricerca.";
        if (productsList) {
            productsList.appendChild(noResultsMsg);
        }

        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            let visibleCount = 0;

            productCards.forEach((card) => {
                const title = card.getAttribute("data-name").toLowerCase();
                const desc = card.getAttribute("data-desc").toLowerCase();

                if (title.includes(query) || desc.includes(query)) {
                    card.style.display = "flex";
                    visibleCount++;
                } else {
                    card.style.display = "none";
                }
            });

            // Mostra o nascondi il messaggio di nessun risultato
            if (visibleCount === 0) {
                noResultsMsg.style.display = "block";
            } else {
                noResultsMsg.style.display = "none";
            }
        });
    }

    // 2. Conferma per il reset della configurazione
    const clearBtn = document.querySelector(".js-clear-build");
    if (clearBtn) {
        clearBtn.addEventListener("click", (e) => {
            const confirmClear = confirm("Sei sicuro di voler resettare e cancellare tutti i componenti scelti finora?");
            if (!confirmClear) {
                e.preventDefault();
            }
        });
    }
});
