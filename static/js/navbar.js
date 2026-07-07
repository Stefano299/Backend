document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('[data-js="navbar"]');
    const navToggle = document.querySelector('[data-js="nav-toggle"]');
    const navLinks = document.querySelector('[data-js="nav-links"]');
    
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navToggle.classList.toggle('active');
            navLinks.classList.toggle('active');
            document.body.classList.toggle('nav-open');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (navLinks.classList.contains('active') && !navLinks.contains(e.target) && !navToggle.contains(e.target)) {
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('nav-open');
            }
        });
        
        // Close menu when clicking on a link or button
        const links = navLinks.querySelectorAll('a, button, form');
        links.forEach(link => {
            link.addEventListener('click', function() {
                navToggle.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('nav-open');
            });
        });
    }

    if (navbar) {
        let lastScrollTop = 0;
        const scrollThreshold = 80;
        
        window.addEventListener('scroll', function() {
            // If mobile menu is active, don't hide the navbar
            if (navLinks && navLinks.classList.contains('active')) {
                return;
            }
            
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
