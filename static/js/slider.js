document.addEventListener('DOMContentLoaded', function() {
    const minSlider = document.getElementById('min-price-slider');
    const maxSlider = document.getElementById('max-price-slider');
    const priceDisplay = document.getElementById('price-range-display');
    const track = document.querySelector('.slider-track');
    
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
            
            // Colora la barra tra i due pallini
            track.style.background = `linear-gradient(to right, #e5e7eb ${minPercent}%, #4f46e5 ${minPercent}%, #4f46e5 ${maxPercent}%, #e5e7eb ${maxPercent}%)`;
            
            // Aggiorna il testo a schermo
            priceDisplay.textContent = `€${finalMin} - €${finalMax}`;
        }
        
        minSlider.addEventListener('input', updateSlider);
        maxSlider.addEventListener('input', updateSlider);
        
        // Inizializzazione
        updateSlider();
    }
});
