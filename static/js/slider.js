// Attende il caricamento completo del DOM
document.addEventListener('DOMContentLoaded', function() {
    const minSlider = document.querySelector('[data-js="min-price-slider"]');
    const maxSlider = document.querySelector('[data-js="max-price-slider"]');
    const priceDisplay = document.querySelector('[data-js="price-range-display"]');
    const track = document.querySelector('[data-js="slider-track"]');
    const container = document.querySelector('[data-js="double-slider-container"]');
    
    // Gestione del cursore a doppio range (slider per il prezzo minimo e massimo)
    if (minSlider && maxSlider && priceDisplay && track) {
        
        function updateSlider() {
            let minVal = parseInt(minSlider.value);
            let maxVal = parseInt(maxSlider.value);
            
            if (minVal > maxVal) {
                minSlider.value = maxVal;
                minVal = maxVal;
            }
            // Serve a rendere la barra tra i due pallini gialla anzichè grigia (il colore del background)
            const maxLimit = parseInt(minSlider.max) || 1000;
            const minPercent = (minVal / maxLimit) * 100;
            const maxPercent = (maxVal / maxLimit) * 100;
            
            track.style.background = `linear-gradient(to right, #3f3f46 ${minPercent}%, #eab308 ${minPercent}%, #eab308 ${maxPercent}%, #3f3f46 ${maxPercent}%)`;
            
            priceDisplay.textContent = `€${minVal} - €${maxVal}`;
        }
        
        // Aggiunge i listener per aggiornare lo slider ogni volta che l'utente sposta i range
        minSlider.addEventListener('input', updateSlider);
        maxSlider.addEventListener('input', updateSlider);
        
        // Cambia dinamicamente lo z-index a seconda di quale pallino sia più vicino al puntatore del mouse.
        // Questo serve ad evitare che un pallino rimanga bloccato sotto l'altro quando hanno lo stesso valore.
        if (container) {
            container.addEventListener('mousemove', function(e) {
                const rect = container.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const width = rect.width;
                const percent = mouseX / width;
                const value = percent * parseInt(minSlider.max);
                
                const minDiff = Math.abs(parseInt(minSlider.value) - value);
                const maxDiff = Math.abs(parseInt(maxSlider.value) - value);
                
                if (minDiff < maxDiff) {
                    minSlider.style.zIndex = '3';
                    maxSlider.style.zIndex = '2';
                } else {
                    maxSlider.style.zIndex = '3';
                    minSlider.style.zIndex = '2';
                }
            });
        }
        
        // Inizializza lo stato dello slider all'avvio della pagina
        updateSlider();
    }
});
