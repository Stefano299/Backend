document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('[data-js="navbar"]');
    const navToggle = document.querySelector('[data-js="nav-toggle"]');
    const navLinks = document.querySelector('[data-js="nav-links"]');
    
    // Gestione dell'apertura/chiusura del menu mobile
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function(e) {
            e.stopPropagation(); 
            navToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
            document.body.classList.toggle('nav-open');
        });
        
        // Chiude il menu mobile se si clicca all'esterno del menu
        document.addEventListener('click', function(e) {
            if (navLinks.classList.contains('active') && !navLinks.contains(e.target) && !navToggle.contains(e.target)) {
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('nav-open');
            }
        });
        
        // Chiude il menu mobile quando si clicca su uno dei suoi link o pulsanti
        const links = navLinks.querySelectorAll('a, button, form');
        links.forEach(function(link) {
            link.addEventListener('click', function() {
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('nav-open');
            });
        });
    }

    // Gestione della scomparsa/comparsa della navbar durante lo scorrimento 
    if (navbar) {
        let lastScrollTop = 0;
        const scrollThreshold = 80;
        
        window.addEventListener('scroll', function() {
            // Se il menu mobile è aperto, non nasconde la navbar
            if (navLinks && navLinks.classList.contains('active')) {
                return;
            }
            
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > scrollThreshold) {
                navbar.classList.add('navbar-hidden');
            } else {
                navbar.classList.remove('navbar-hidden');
            }
            
            lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
        });
    }
});
