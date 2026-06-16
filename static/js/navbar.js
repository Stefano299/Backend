document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('[data-js="navbar"]');
    
    if (navbar) {
        let lastScrollTop = 0;
        const scrollThreshold = 80;
        
        window.addEventListener('scroll', function() {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > scrollThreshold) {
                // Scorrendo verso il basso: nasconde la navbar
                navbar.classList.add('navbar-hidden');
            } else {
                // Scorrendo verso l'alto: mostra la navbar
                navbar.classList.remove('navbar-hidden');
            }
            
            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
        }, { passive: true });
    }
});
