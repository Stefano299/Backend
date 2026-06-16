document.addEventListener('DOMContentLoaded', function() {
    const minusBtn = document.querySelector('[data-js="qty-minus"]');
    const plusBtn = document.querySelector('[data-js="qty-plus"]');
    const input = document.querySelector('[data-js="qty-input"]');
    
    if (minusBtn && plusBtn && input) {
        const minVal = parseInt(input.getAttribute('min')) || 1;
        const maxVal = parseInt(input.getAttribute('max')) || 999;
        
        minusBtn.addEventListener('click', function() {
            let currentVal = parseInt(input.value) || minVal;
            if (currentVal > minVal) {
                input.value = currentVal - 1;
            }
        });
        
        plusBtn.addEventListener('click', function() {
            let currentVal = parseInt(input.value) || minVal;
            if (currentVal < maxVal) {
                input.value = currentVal + 1;
            }
        });
    }
});
