document.addEventListener('DOMContentLoaded', function() {
    const minSlider = document.querySelector('[data-js="min-price-slider"]');
    const maxSlider = document.querySelector('[data-js="max-price-slider"]');
    const priceDisplay = document.querySelector('[data-js="price-range-display"]');
    const track = document.querySelector('[data-js="slider-track"]');
    const container = document.querySelector('[data-js="double-slider-container"]');
    
    if (minSlider && maxSlider && priceDisplay && track) {
        function updateSlider() {
            const minVal = parseInt(minSlider.value);
            const maxVal = parseInt(maxSlider.value);
            
            // Impedisce l'incrocio dei pallini
            if (minVal > maxVal) {
                minSlider.value = maxVal;
            }
            
            const finalMin = minSlider.value;
            const finalMax = maxSlider.value;
            
            // Calcola le percentuali per colorare la barra centrale
            const minPercent = (finalMin / minSlider.max) * 100;
            const maxPercent = (finalMax / maxSlider.max) * 100;
            
            // Colora la barra tra i due pallini con colore giallo chiaro (#fde047) e sfondo grigio scuro (#27272a)
            track.style.background = `linear-gradient(to right, #27272a ${minPercent}%, #fde047 ${minPercent}%, #fde047 ${maxPercent}%, #27272a ${maxPercent}%)`;
            
            // Aggiorna il testo a schermo
            priceDisplay.textContent = `€${finalMin} - €${finalMax}`;
        }
        
        minSlider.addEventListener('input', updateSlider);
        maxSlider.addEventListener('input', updateSlider);
        
        // Cambia dinamicamente lo z-index a seconda di quale pallino sia più vicino al cursore del mouse
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
        
        // Inizializzazione
        updateSlider();
    }
});
