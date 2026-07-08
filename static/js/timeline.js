document.addEventListener("DOMContentLoaded", function() {
    const progressLine = document.querySelector('[data-js="progress-line"]');
    const items = document.querySelectorAll('[data-js="timeline-item"]');
    
    // Funzione che calcola e disegna la linea verticale di progresso tra i punti della timeline
    function updateProgressLine() {
        if (!progressLine || items.length === 0) return;
        
        let activeIndex = -1;
        
        // Trova l'ultimo elemento attivo o completato nella timeline
        items.forEach(function(item, index) {
            if (item.classList.contains("active")) {
                activeIndex = index;
            } else if (item.classList.contains("completed") && index > activeIndex) {
                activeIndex = index;
            }
        });

        if (activeIndex >= 0) {
            const firstBullet = items[0].querySelector('[data-js="timeline-bullet"]');
            const activeBullet = items[activeIndex].querySelector('[data-js="timeline-bullet"]');
            
            const timeline = document.querySelector('[data-js="timeline"]');
            if (!timeline || !firstBullet || !activeBullet) return;
            
            // Ottiene le posizioni degli elementi rispetto al viewport
            const timelineRect = timeline.getBoundingClientRect();
            const firstRect = firstBullet.getBoundingClientRect();
            const activeRect = activeBullet.getBoundingClientRect();
            
            // Calcola la distanza dall'alto per l'inizio e la fine della linea di progresso
            const startTop = (firstRect.top + firstRect.height / 2) - timelineRect.top;
            const endTop = (activeRect.top + activeRect.height / 2) - timelineRect.top;
            const height = endTop - startTop;
            
            // Aggiorna lo stile css della linea verticale di progresso
            progressLine.style.top = startTop + "px";
            progressLine.style.height = height + "px";
        } else {
            progressLine.style.height = "0px";
        }
    }
    
    // Attende un brevissimo intervallo per permettere al browser di renderizzare gli elementi prima del calcolo
    setTimeout(updateProgressLine, 100);
    
    // Ricalcola la linea di progresso in caso di ridimensionamento della finestra
    window.addEventListener("resize", updateProgressLine);
});
